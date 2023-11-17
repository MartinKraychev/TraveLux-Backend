from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from jose import jwt

from datetime import datetime
import crud
import models
import schemas
from auth_bearer import JWTBearer

from database import SessionLocal, engine
from utils import verify_password, create_access_token, token_required, is_property_owner

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

JWT_SECRET_KEY = "57fa348014a82862718ea6825f6b71692b465e0ca0c68c8e75f23155c6cf0a4e"
ALGORITHM = "HS256"


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user_with_email = crud.get_user_by_email(db, email=user.email)
    if db_user_with_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user_with_phone_number = crud.get_user_by_phone_number(db, phone_number=user.phone_number)
    if db_user_with_phone_number:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    return crud.create_user(db=db, user=user)


@app.post('/login', summary="Create access and refresh tokens for user", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user_with_email = crud.get_user_by_email(db, email=user.email)
    if db_user_with_email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = db_user_with_email.hashed_password
    if not verify_password(user.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    access = create_access_token(db_user_with_email.id)
    crud.create_token(db=db, user_id=db_user_with_email.id, access_token=access, status=True)

    return {
        "access_token": access,
    }


@app.post('/logout')
@token_required
def logout(dependencies=Depends(JWTBearer()), db: Session = Depends(get_db)):
    token = dependencies
    payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
    user_id = payload['sub']
    token_records = db.query(models.Token).all()
    expired_tokens = []

    for record in token_records:
        if (datetime.utcnow() - record.created_date).days > 1:
            expired_tokens.append(record.user_id)

    if expired_tokens:
        crud.delete_expired_tokens(db, expired_tokens)

    crud.set_inactive_token(db, user_id, token)

    return {"message": "Logout Successfully"}


@app.get("/users/{user_id}", response_model=schemas.User)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/properties/", response_model=schemas.Property)
@token_required
def create_property(prop: schemas.PropertyCreate, dependencies=Depends(JWTBearer()), db: Session = Depends(get_db)):
    return crud.create_property(db=db, prop=prop, token=dependencies)


@app.get("/properties/", response_model=list[schemas.Property])
def get_properties(db: Session = Depends(get_db)):
    properties = crud.get_properties(db)
    return properties


@app.get("/properties/{property_id}/edit", response_model=schemas.Property)
@token_required
def edit_property(property_id: int, dependencies=Depends(JWTBearer()), db: Session = Depends(get_db)):
    prop = crud.get_property(db, property_id)
    if prop is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@app.patch("/properties/{property_id}/edit", response_model=schemas.Property)
@token_required
@is_property_owner
def edit_property(property_id: int, prop_data: schemas.PropertyCreate, dependencies=Depends(JWTBearer()), db: Session = Depends(get_db)):
    prop = crud.get_property(db, property_id)
    return crud.edit_property(db, prop, prop_data)


@app.delete("/properties/{property_id}/delete")
@token_required
@is_property_owner
def delete_property(property_id: int, dependencies=Depends(JWTBearer()), db: Session = Depends(get_db)):
    crud.delete_property(db, property_id)
    return {'message': 'Property deleted successfully'}


@app.get("/my-properties/", response_model=list[schemas.Property])
@token_required
def get_my_properties(dependencies=Depends(JWTBearer()), db: Session = Depends(get_db)):
    properties = crud.get_my_properties(db, dependencies)
    return properties


@app.get("/properties/{property_id}", response_model=schemas.Property)
def get_property_by_id(property_id: int, db: Session = Depends(get_db)):
    prop = crud.get_property(db, property_id)
    if prop is None:
        raise HTTPException(status_code=404, detail="Property not found")

    # Calculate average rating
    average_rating = sum([rate.vote for rate in prop.ratings]) / len(prop.ratings) if prop.ratings else 0.0

    # Create a dictionary representation of the model
    prop_dict = prop.__dict__

    # Remove any keys that are not part of the Pydantic model
    prop_dict.pop('_sa_instance_state', None)

    # Add the average_rating to the dictionary
    prop_dict['average_rating'] = average_rating

    # Create an instance of the Pydantic model
    response_model = schemas.Property(**prop_dict)

    return response_model


@app.post("/properties/{property_id}/rate")
@token_required
def rate_property(rate: schemas.Rate, property_id: int, dependencies=Depends(JWTBearer()), db: Session = Depends(get_db)):
    prop = crud.get_property(db, property_id)
    if prop is None:
        raise HTTPException(status_code=404, detail="Property not found")

    payload = jwt.decode(dependencies, JWT_SECRET_KEY, ALGORITHM)
    user_id = payload['sub']
    if int(user_id) == prop.owner_id:
        raise HTTPException(status_code=403, detail="Can not rate own property")

    rating = crud.get_rating(db, property_id, user_id)
    if rating:
        raise HTTPException(status_code=403, detail="You already rated this property")

    crud.create_rating(db, property_id, user_id, rate)
    return {"message": "Rated this property successfully"}


@app.post("/check-rating")
@token_required
def check_rating(rate: schemas.CheckRate, dependencies=Depends(JWTBearer()), db: Session = Depends(get_db)):
    rating = crud.get_rating(db, rate.property_id, rate.user_id)
    return bool(rating)


# Todo
# file storage?
# Docs, refactor


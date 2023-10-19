from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud
import models
import schemas

from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user_with_email = crud.get_user_by_email(db, email=user.email)
    if db_user_with_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user_with_phone_number = crud.get_user_by_phone_number(db, phone_number=user.phone_number)
    if db_user_with_phone_number:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    return crud.create_user(db=db, user=user)


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/properties/", response_model=schemas.Property)
def create_property(prop: schemas.PropertyCreate, db: Session = Depends(get_db)):
    return crud.create_property(db=db, prop=prop)


@app.get("/properties/", response_model=list[schemas.Property])
def get_properties(db: Session = Depends(get_db)):
    properties = crud.get_properties(db)
    return properties

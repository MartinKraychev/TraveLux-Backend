from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette import status

from auth_bearer import get_token_credentials
import models
import schemas
from database_operations import user_operations, token_operations
from db import get_db
from utils import token_required, verify_password, create_access_token

router = APIRouter()


def authenticate_user(email: str, password: str, db: Session):
    db_user = user_operations.get_user_by_email(db, email=email)
    if db_user is None or not verify_password(password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    return db_user


@router.post("/register/", response_model=schemas.RegisterUser)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if email is already registered
    if user_operations.get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if phone number is already registered
    if user_operations.get_user_by_phone_number(db, phone_number=user.phone_number):
        raise HTTPException(status_code=400, detail="Phone number already registered")

    # Create the user
    db_user = create_user(db=db, user=user)

    # Authenticate the user and generate tokens
    access_token = create_access_token(db_user.id)

    # Save access token to the database
    token_operations.create_token(db=db, user_id=db_user.id, access_token=access_token, status=True)

    user_dict = {
        "id": db_user.id,
        "email": db_user.email,
        "phone_number": db_user.phone_number,
        "is_active": db_user.is_active,
        # Add any other fields you want to include
        "access_token": access_token,
    }

    # Create an instance of the Pydantic model
    response_model = schemas.RegisterUser(**user_dict)
    return response_model


@router.post('/login', summary="Create access and refresh tokens for user", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(user.email, user.password, db)

    # Generate access token
    access_token = create_access_token(db_user.id)

    # Save access token to the database
    token_operations.create_token(db=db, user_id=db_user.id, access_token=access_token, status=True)

    return {"access_token": access_token}


@router.post('/logout')
@token_required
def logout(request: Request, token_credentials=Depends(get_token_credentials), db: Session = Depends(get_db)):
    payload = request.state.current_user
    user_id = payload['sub']
    token_records = db.query(models.Token).all()
    expired_tokens = []

    for record in token_records:
        if (datetime.utcnow() - record.created_date).days > 1:
            expired_tokens.append(record.user_id)

    if expired_tokens:
        token_operations.delete_expired_tokens(db, expired_tokens)

    token_operations.set_inactive_token(db, user_id, token_credentials)

    return {"message": "Logout Successfully"}
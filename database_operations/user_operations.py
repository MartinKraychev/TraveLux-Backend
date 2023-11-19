from sqlalchemy.orm import Session

import models
import schemas
from utils import get_hashed_password


def get_user_by_id(db: Session, user_id: int):
    """
    Gets user by id
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    """
    Gets user by email
    """
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_phone_number(db: Session, phone_number: str):
    """
    Gets user by phone number
    """
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()


def create_user(db: Session, user: schemas.UserCreate):
    """
    Creates a user
    """
    encrypted_password = get_hashed_password(user.password)
    db_user = models.User(email=user.email, hashed_password=encrypted_password, phone_number=user.phone_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

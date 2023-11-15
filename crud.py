from sqlalchemy.orm import Session

import models
import schemas
from utils import get_hashed_password


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_phone_number(db: Session, phone_number: str):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()


def create_user(db: Session, user: schemas.UserCreate):
    encrypted_password = get_hashed_password(user.password)
    db_user = models.User(email=user.email, hashed_password=encrypted_password, phone_number=user.phone_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def create_token(db: Session, user_id, access_token, status):
    token_db = models.Token(user_id=user_id, access_token=access_token, status=status)
    db.add(token_db)
    db.commit()
    db.refresh(token_db)


def delete_expired_tokens(db: Session, tokens):
    db.query(models.Token).where(models.Token.user_id.in_(tokens)).delete()
    db.commit()


def set_inactive_token(db: Session, user_id, token):
    existing_token = db.query(models.Token).filter(models.Token.user_id == user_id,
                                                   models.Token.access_token == token).first()
    if existing_token:
        existing_token.status = False
        db.add(existing_token)
        db.commit()
        db.refresh(existing_token)


def get_property(db: Session, property_id: int):
    return db.query(models.Property).filter(models.Property.id == property_id).first()


def get_properties(db: Session):
    return db.query(models.Property).all()


def create_property(db: Session, prop: schemas.PropertyCreate):
    db_item = models.Property(**prop.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item



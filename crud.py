from sqlalchemy.orm import Session

import models
import schemas


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_phone_number(db: Session, phone_number: str):
    return db.query(models.User).filter(models.User.phone_number == phone_number).first()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password, phone_number=user.phone_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


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



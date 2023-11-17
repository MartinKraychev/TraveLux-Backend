from sqlalchemy.orm import Session

import models
import schemas
from utils import get_hashed_password
from jose import jwt

JWT_SECRET_KEY = "57fa348014a82862718ea6825f6b71692b465e0ca0c68c8e75f23155c6cf0a4e"
ALGORITHM = "HS256"


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


def get_my_properties(db:Session, token):
    payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
    user_id = payload['sub']
    return db.query(models.Property).filter(models.Property.owner_id == user_id)


def create_property(db: Session, prop: schemas.PropertyCreate, token):
    payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
    user_id = payload['sub']
    user = get_user_by_id(db, user_id)
    property_fields = prop.model_dump()
    property_fields['owner_number'] = user.phone_number
    property_fields['owner_id'] = user.id

    db_item = models.Property(**property_fields)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item


def edit_property(db: Session, prop, prop_data):
    prop_data = prop_data.dict(exclude_unset=True)
    for key, value in prop_data.items():
        setattr(prop, key, value)
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


def delete_property(db: Session, property_id):
    prop = get_property(db, property_id)
    db.delete(prop)
    db.commit()


def get_rating(db: Session, property_id, user_id):
    return db.query(models.Rating).filter(models.Rating.owner_id == user_id,
                                          models.Rating.property_id == property_id).first()


def create_rating(db, property_id, user_id, rate):
    rating_fields = rate.model_dump()
    rating_fields['owner_id'] = user_id
    rating_fields['property_id'] = property_id

    db_item = models.Rating(**rating_fields)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item

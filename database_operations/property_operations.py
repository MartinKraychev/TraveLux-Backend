from sqlalchemy.orm import Session

import models
import schemas
from database_operations.user_operations import get_user_by_id


def get_property(db: Session, property_id: int):
    return db.query(models.Property).filter(models.Property.id == property_id).first()


def get_properties(db: Session):
    return db.query(models.Property).all()


def get_my_properties(db: Session, user_id):
    return db.query(models.Property).filter(models.Property.owner_id == user_id)


def create_property(db: Session, prop: schemas.PropertyCreate, user_id):
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
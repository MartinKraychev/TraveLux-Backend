from sqlalchemy.orm import Session

import models


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
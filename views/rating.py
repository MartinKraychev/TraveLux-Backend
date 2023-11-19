from fastapi import APIRouter
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database_operations import rating_operations, property_operations
from auth_bearer import get_token_credentials

import schemas
from db import get_db
from decorators import token_required

router = APIRouter()


@router.post("/check-rating")
@token_required
def can_rate(request: Request,
             rate: schemas.CheckRate,
             token_credentials=Depends(get_token_credentials),
             db: Session = Depends(get_db)):
    """
    Checks if user can rate a property
    """

    prop = property_operations.get_property(db, rate.property_id)
    if prop is None:
        return False

    if int(rate.user_id) == prop.owner_id:
        return False

    rating = rating_operations.get_rating(db, rate.property_id, rate.user_id)
    if rating:
        return False

    return True


@router.post("/{property_id}")
@token_required
def rate_property(request: Request,
                  rate: schemas.Rate, property_id: int,
                  token_credentials=Depends(get_token_credentials),
                  db: Session = Depends(get_db)):
    """
    Property rating by user
    """

    prop = property_operations.get_property(db, property_id)
    if prop is None:
        raise HTTPException(status_code=404, detail="Property not found")

    payload = request.state.current_user
    user_id = payload['sub']
    if int(user_id) == prop.owner_id:
        raise HTTPException(status_code=403, detail="Can not rate own property")

    rating = rating_operations.get_rating(db, property_id, user_id)
    if rating:
        raise HTTPException(status_code=403, detail="You already rated this property")

    rating_operations.create_rating(db, property_id, user_id, rate)
    return {"message": "Rated this property successfully"}


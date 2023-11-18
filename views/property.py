from fastapi import APIRouter
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from auth_bearer import get_token_credentials

import schemas
from database_operations import property_operations
from db import get_db
from utils import token_required, is_property_owner

router = APIRouter()


@router.post("/", response_model=schemas.Property)
@token_required
def create_property(request: Request,
                    prop: schemas.PropertyCreate,
                    token_credentials=Depends(get_token_credentials),
                    db: Session = Depends(get_db)):

    payload = request.state.current_user
    user_id = payload['sub']
    return property_operations.create_property(db=db, prop=prop, user_id=user_id)


@router.get("/", response_model=list[schemas.Property])
def get_properties(db: Session = Depends(get_db)):
    properties = property_operations.get_properties(db)
    return properties


@router.get("/{property_id}", response_model=schemas.Property)
def get_property_by_id(property_id: int, db: Session = Depends(get_db)):
    prop = property_operations.get_property(db, property_id)
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


@router.get("/{property_id}/edit", response_model=schemas.Property)
@token_required
def edit_property(request: Request,
                  property_id: int,
                  token_credentials=Depends(get_token_credentials),
                  db: Session = Depends(get_db)):

    prop = property_operations.get_property(db, property_id)
    if prop is None:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.patch("/{property_id}/edit", response_model=schemas.Property)
@token_required
@is_property_owner
def edit_property(request: Request,
                  property_id: int,
                  prop_data: schemas.PropertyCreate,
                  token_credentials=Depends(get_token_credentials),
                  db: Session = Depends(get_db)):

    prop = property_operations.get_property(db, property_id)
    return property_operations.edit_property(db, prop, prop_data)


@router.delete("/{property_id}/delete")
@token_required
@is_property_owner
def delete_property(request: Request,
                    property_id: int,
                    token_credentials=Depends(get_token_credentials),
                    db: Session = Depends(get_db)):

    property_operations.delete_property(db, property_id)
    return {'message': 'Property deleted successfully'}


@router.get("/my-properties", response_model=list[schemas.Property])
@token_required
def get_my_properties(request: Request,
                      token_credentials=Depends(get_token_credentials),
                      db: Session = Depends(get_db)):

    payload = request.state.current_user
    user_id = payload['sub']
    properties = property_operations.get_my_properties(db, user_id)
    return properties

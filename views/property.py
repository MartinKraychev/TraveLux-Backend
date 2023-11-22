from fastapi import APIRouter
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from auth_bearer import get_token_credentials

import schemas
from database_operations import property_operations
from db import get_db
from decorators import token_required, is_property_owner
from utils import attach_average_rating

router = APIRouter()


@router.post("/", response_model=schemas.Property)
@token_required
def create_property(request: Request,
                    prop: schemas.PropertyCreate,
                    token_credentials=Depends(get_token_credentials),
                    db: Session = Depends(get_db)):
    """
    Creates a new property with ownership of the given user
    """

    payload = request.state.current_user
    user_id = payload['sub']
    return property_operations.create_property(db=db, prop=prop, user_id=user_id)


@router.get("/", response_model=list[schemas.PropertyWithRating])
def get_properties(db: Session = Depends(get_db)):
    """
    Gets all properties and adds average rating for each
    """
    properties = property_operations.get_properties(db)
    modified_properties = []
    for prop in properties:
        modified_properties.append(attach_average_rating(prop))

    return modified_properties


@router.get("/my-properties", response_model=list[schemas.PropertyWithRating])
@token_required
def get_my_properties(request: Request,
                      token_credentials=Depends(get_token_credentials),
                      db: Session = Depends(get_db)):

    """
    Gets user properties and adds average rating for each
    """

    payload = request.state.current_user
    user_id = payload['sub']
    properties = property_operations.get_my_properties(db, user_id)
    modified_properties = []

    for prop in properties:
        modified_properties.append(attach_average_rating(prop))

    return modified_properties


@router.get("/{property_id}", response_model=schemas.PropertyWithRating)
def get_property_by_id(property_id: int, db: Session = Depends(get_db)):
    """
    Gets property by id and adds average rating for it
    """
    prop = property_operations.get_property(db, property_id)
    if prop is None:
        raise HTTPException(status_code=404, detail="Property not found")

    # Create an instance of the Pydantic model
    response_model = attach_average_rating(prop)

    return response_model


@router.put("/{property_id}/edit", response_model=schemas.Property)
@token_required
@is_property_owner
def edit_property(request: Request,
                  property_id: int,
                  prop_data: schemas.PropertyCreate,
                  token_credentials=Depends(get_token_credentials),
                  db: Session = Depends(get_db)):
    """
    Edit property
    """

    prop = property_operations.get_property(db, property_id)
    return property_operations.edit_property(db, prop, prop_data)


@router.delete("/{property_id}/delete")
@token_required
@is_property_owner
def delete_property(request: Request,
                    property_id: int,
                    token_credentials=Depends(get_token_credentials),
                    db: Session = Depends(get_db)):
    """
    Delete property
    """

    property_operations.delete_property(db, property_id)
    return {'message': 'Property deleted successfully'}

from functools import wraps

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

import models
from database_operations.property_operations import get_property


def token_required(func):
    """
    Verifies that a token is valid
    """
    @wraps(func)
    def wrapper(*args, request: Request, **kwargs):
        payload = request.state.current_user
        user_id = payload['sub']
        data = kwargs['db'].query(models.Token).filter_by(user_id=user_id,
                                                          access_token=kwargs['token_credentials'],
                                                          status=True).first()
        if data:
            return func(request=request, **kwargs)

        else:
            return JSONResponse(content={"msg": "Token blocked"}, status_code=403)

    return wrapper


def is_property_owner(func):
    """
    Checks if the property is owned by the user
    """
    @wraps(func)
    def wrapper(*args, request: Request, **kwargs):
        db = kwargs['db']
        property_id = kwargs['property_id']
        prop = get_property(db, property_id)

        if prop is None:
            raise HTTPException(status_code=404, detail="Property not found")

        payload = request.state.current_user
        user_id = payload['sub']

        if int(user_id) != prop.owner_id:
            raise HTTPException(status_code=403, detail="Unauthorised")

        return func(request=request, **kwargs)

    return wrapper

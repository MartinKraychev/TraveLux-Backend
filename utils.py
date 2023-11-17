from functools import wraps

from fastapi import HTTPException, Request
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from fastapi.responses import JSONResponse

import crud
import models


JWT_SECRET_KEY = "57fa348014a82862718ea6825f6b71692b465e0ca0c68c8e75f23155c6cf0a4e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 180  # 30 minutes

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password):
    return password_context.hash(password)


def verify_password(password, hashed_pass):
    return password_context.verify(password, hashed_pass)


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def token_required(func):
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
    @wraps(func)
    def wrapper(*args, request: Request, **kwargs):
        db = kwargs['db']
        property_id = kwargs['property_id']
        prop = crud.get_property(db, property_id)

        if prop is None:
            raise HTTPException(status_code=404, detail="Property not found")

        payload = request.state.current_user
        user_id = payload['sub']

        if int(user_id) != prop.owner_id:
            raise HTTPException(status_code=403, detail="Unauthorised")

        return func(request=request, **kwargs)

    return wrapper

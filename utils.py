from functools import wraps

from fastapi import HTTPException
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt

import crud
import models


JWT_SECRET_KEY = "57fa348014a82862718ea6825f6b71692b465e0ca0c68c8e75f23155c6cf0a4e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days

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
    def wrapper(*args, **kwargs):

        payload = jwt.decode(kwargs['dependencies'], JWT_SECRET_KEY, ALGORITHM)
        user_id = payload['sub']
        data = kwargs['db'].query(models.Token).filter_by(user_id=user_id,
                                                          access_token=kwargs['dependencies'],
                                                          status=True).first()
        if data:
            return func(**kwargs)

        else:
            return {'msg': "Token blocked"}

    return wrapper


def is_property_owner(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        db = kwargs['db']
        property_id = kwargs['property_id']
        prop = crud.get_property(db, property_id)

        if prop is None:
            raise HTTPException(status_code=404, detail="Property not found")

        payload = jwt.decode(kwargs['dependencies'], JWT_SECRET_KEY, ALGORITHM)
        user_id = payload['sub']

        if int(user_id) != prop.owner_id:
            raise HTTPException(status_code=403, detail="Unauthorised")

        return func(**kwargs)

    return wrapper

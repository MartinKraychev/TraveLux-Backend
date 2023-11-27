from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt


JWT_SECRET_KEY = "57fa348014a82862718ea6825f6b71692b465e0ca0c68c8e75f23155c6cf0a4e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 180  # 180 minutes

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password):
    """
    Hashes password
    """
    return password_context.hash(password)


def verify_password(password, hashed_pass):
    """
    Compares hash of password against password
    """
    return password_context.verify(password, hashed_pass)


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    Creates access token
    """
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def attach_average_rating(prop):
    """
    Gets the avg rating of a prop
    """
    # Calculate average rating
    average_rating = sum([rate.vote for rate in prop.ratings]) / len(prop.ratings) if prop.ratings else 0.0

    # Create a dictionary representation of the model
    prop_dict = prop.__dict__

    # Remove any keys that are not part of the Pydantic model
    prop_dict.pop('_sa_instance_state', None)

    # Add the average_rating to the dictionary
    prop_dict['average_rating'] = round(average_rating, 1)
    return prop_dict

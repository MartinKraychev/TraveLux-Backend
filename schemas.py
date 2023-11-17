from typing import Literal

from pydantic import BaseModel


class PropertyBase(BaseModel):
    title: str
    type: Literal['Flat', 'Vila', 'House']
    image_url: str
    price_per_night: float
    address: str
    summary: str
    location: Literal['Usa', 'Europe', 'Australia']


class PropertyCreate(PropertyBase):
    pass


class Property(PropertyBase):
    id: int
    average_rating: float
    owner_number: str

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: str
    phone_number: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class RegisterUser(User):
    access_token: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str


class Rate(BaseModel):
    vote: Literal['1', '2', '3', '4', '5']


class CheckRate(BaseModel):
    user_id: int
    property_id: int

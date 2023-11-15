from typing import Literal

from pydantic import BaseModel


class PropertyBase(BaseModel):
    title: str
    type: Literal['Flat', 'Vila', 'House']
    image_url: str
    price_per_night: float
    address: str
    owner_number: str
    summary: str
    location: Literal['Usa', 'Europe', 'Australia']
    owner_id: int


class PropertyCreate(PropertyBase):
    pass


class Property(PropertyBase):
    id: int

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


class Token(BaseModel):
    access_token: str
    refresh_token: str

from pydantic import BaseModel


class PropertyBase(BaseModel):
    title: str
    type: str
    image_url: str
    price_per_night: float
    address: str
    owner_number: str
    summary: str
    location: str


class PropertyCreate(PropertyBase):
    pass


class Property(PropertyBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: str
    phone_number: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    properties: list[Property] = []

    class Config:
        from_attributes = True

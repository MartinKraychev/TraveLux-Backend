from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    properties = relationship("Property", back_populates="owner")
    ratings = relationship("Rating", back_populates="owner")


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    type = Column(String, index=True)
    image_url = Column(String, index=True)
    # img -> cloudinary
    price_per_night = Column(Float, index=True)
    address = Column(String, index=True)
    owner_number = Column(String, index=True)
    summary = Column(String, index=True)
    location = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="properties")
    ratings = relationship("Rating", back_populates="property")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    vote = Column(Integer, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    property_id = Column(Integer, ForeignKey("properties.id"))

    owner = relationship("User", back_populates="ratings")
    property = relationship("Property", back_populates="ratings")





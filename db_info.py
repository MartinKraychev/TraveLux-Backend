from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://my_user:4295aHUJXgQzkBbasijrt7ogw8pmku6x@dpg-cll15g4jtl8s73f580a0-a.frankfurt-postgres.render.com/travelux_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

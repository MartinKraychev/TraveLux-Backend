from fastapi import FastAPI

import models

from views.auth import router as auth_router
from views.property import router as property_router
from views.rating import router as rating_router
from db_info import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(property_router, prefix="/properties", tags=["properties"])
app.include_router(rating_router, prefix="/rate", tags=["rate"])

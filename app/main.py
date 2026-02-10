from fastapi import FastAPI
from .database import engine
from .model import Base
import app.routers as routers 


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(routers.router)
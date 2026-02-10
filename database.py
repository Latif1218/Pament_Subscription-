from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)

sessionalocal = sessionmaker(autocommit=False,autoflush=False, bind=engine)

base = declarative_base()

def get_db():
    db = sessionalocal()
    try:
        yield db
    finally:
        db.close()
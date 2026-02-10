from sqlalchemy import Column, Integer, String,Float
from .database import Base

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    email = Column(String)
    name = Column(String, nullable=True)
    amount = Column(Float)
    currency = Column(String)
    payment_status = Column(String)
    user_id = Column(Integer)
    request_id = Column(String)
    
    
from sqlalchemy import Column, Integer, String,Float, DateTime, func
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
    
    
    
class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    email = Column(String, index=True)
    stripe_customer_id = Column(String, index=True)
    stripe_subscription_id = Column(String, unique=True, index=True)
    stripe_price_id = Column(String)
    status = Column(String) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    
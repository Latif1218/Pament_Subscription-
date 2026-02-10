from pydantic import BaseModel, EmailStr

class PaymentCreate(BaseModel):
    session_id: str
    email: str
    name: str | None
    amount: float
    currency: str
    payment_status: str
    user_id: str
    request_id: str
    
class CheckoutRequest(BaseModel):
    price: int
    email: EmailStr
    user_id: int
    request_id: int
    
    
    
    
    
class CheckoutSubscriptionRequest(BaseModel):
    price_id: str
    email: EmailStr
    user_id: int


class SubscriptionOut(BaseModel):
    id: int
    user_id: int
    email: EmailStr
    status: str

    class Config:
        from_attributes = True
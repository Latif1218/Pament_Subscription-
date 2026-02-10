import json
import stripe
from fastapi import APIRouter, Request, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from .database import get_db
from .model import Payment
from .schemas import PaymentCreate, CheckoutRequest
from dotenv import load_dotenv
from .config import STRIPE_SECRET_KEY, BASE_URL

stripe.api_key = STRIPE_SECRET_KEY


router = APIRouter(
    tags=["Payment"],
    prefix="/payment"
)

@router.post("/checkout")
async def create_checkout_session(data: CheckoutRequest):
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "FastAPI Stripe Checkout",
                        },
                        "unit_amount": data.price * 100,
                    },
                    "quantity": 1,
                }
            ],
            metadata={
                "user_id": data.user_id,
                "email": data.email,
                "request_id": data.request_id
            },
            mode="payment",
            success_url=BASE_URL + "/success/?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=BASE_URL + "/cancel/",
            customer_email=data.email,
        )
        print("Checkout URL:", checkout_session.url)
        return {"checkout_url":checkout_session.url}
    
    except Exception as e:
        print("Stripr error:", str(e))
        raise HTTPException(status_code=500, detail="Stripe session creation failed")




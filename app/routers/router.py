import json
import stripe
from fastapi import APIRouter, Request, HTTPException, status, Form, Depends, Query
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..model import Subscription
from ..config import (
    STRIPE_SECRET_KEY,
    DOMAIN,
    STRIPE_WEBHOOK_SECRET,
    STRIPE_PUBLISHABLE_KEY,
    STRIPE_MONTHLY_PRICE_ID,
    STRIPE_YEARLY_PRICE_ID
)

stripe.api_key = STRIPE_SECRET_KEY
stripe.api_version = "2024-06-20"

router = APIRouter(tags=["Subscription"])  # NO prefix

# Config
@router.get("/config")
async def get_config():
    return {
        "publishableKey": STRIPE_PUBLISHABLE_KEY,
        "monthlyPrice": STRIPE_MONTHLY_PRICE_ID,
        "yearlyPrice": STRIPE_YEARLY_PRICE_ID,
    }

# Create Checkout Session
@router.post("/checkout")
async def create_checkout_session(
    price_id: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            metadata={
                "user_id": "demo_user_123",      # ← change to real user_id from auth
                "email": "demo@example.com"      # ← change to real email
            },
            success_url=f"{DOMAIN.rstrip('/')}/static/success.html?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{DOMAIN.rstrip('/')}/static/canceled.html",
        )
        subscription = Subscription(
            user_id=123,                         
            email="demo@example.com",
            stripe_customer_id=session.customer,
            stripe_subscription_id=session.subscription,
            stripe_price_id=price_id,
            status="active"                      
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)

        print(f"subscription is save in database: {subscription.id}")
        return RedirectResponse(session.url, status_code=status.HTTP_303_SEE_OTHER)
    except stripe.error.StripeError as e:
        return JSONResponse(status_code=400, content={"error": {"message": str(e)}})

# Get Checkout Session
@router.get("/checkout-session")
async def get_checkout_session(sessionId: str = Query(...)):
    try:
        return stripe.checkout.Session.retrieve(sessionId)
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Customer Portal
@router.post("/customer-portal")
async def customer_portal(sessionId: str = Form(...)):
    try:
        checkout_session = stripe.checkout.Session.retrieve(sessionId)
        if not checkout_session.customer:
            raise ValueError("No customer found")
        portal = stripe.billing_portal.Session.create(
            customer=checkout_session.customer,
            return_url=DOMAIN
        )
        return RedirectResponse(portal.url, status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Webhook
@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not STRIPE_WEBHOOK_SECRET:
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    else:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        except Exception as e:
            raise HTTPException(400, str(e))

    if event.type == "checkout.session.completed":
        session = event.data.object
        if session.mode == "subscription":
            metadata = session.metadata or {}
            if "user_id" not in metadata:
                return {"status": "success"}
            try:
                user_id = int(metadata["user_id"])
                email = metadata.get("email", "")
                price_id = session.line_items.data[0].price.id if session.line_items.data else None

                sub = Subscription(
                    user_id=user_id,
                    email=email,
                    stripe_customer_id=session.customer,
                    stripe_subscription_id=session.subscription,
                    stripe_price_id=price_id,
                    status="active"
                )
                db.add(sub)
                db.commit()
                print(f"Subscription saved → user {user_id}")
            except Exception as e:
                print(f"DB error: {e}")

    return {"status": "success"}
from fastapi import APIRouter, Request, HTTPException
import stripe
from src.monetization.stripe_client import StripeClient
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhook", tags=["webhook"])


@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, stripe.webhook_secret)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event.type
    data = event.data.object

    logger.info(f"Stripe webhook received: {event_type}")

    if event_type == "checkout.session.completed":
        session = data
        logger.info(f"Checkout completed: {session.id} | customer={session.customer}")
        return {"status": "success", "event": event_type}

    elif event_type == "customer.subscription.created":
        logger.info(f"Subscription created: {data.id} | status={data.status}")

    elif event_type == "customer.subscription.updated":
        logger.info(f"Subscription updated: {data.id} | status={data.status}")

    elif event_type == "customer.subscription.deleted":
        logger.info(f"Subscription deleted: {data.id}")

    elif event_type == "invoice.paid":
        logger.info(f"Invoice paid: {data.id} | amount={data.amount_paid}")

    elif event_type == "invoice.payment_failed":
        logger.warning(f"Invoice payment failed: {data.id}")

    return {"status": "success", "event": event_type}


@router.post("/stripe/connect")
async def stripe_connect_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, stripe.connect_webhook_secret)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook")

    logger.info(f"Stripe Connect webhook: {event.type}")
    return {"status": "success", "event": event.type}

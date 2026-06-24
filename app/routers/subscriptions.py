from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from src.monetization.plans import PLANS, get_plan

router = APIRouter()


@router.get("/plans")
async def list_plans():
    return {"plans": PLANS}


@router.get("/plans/{plan_id}")
async def get_plan_by_id(plan_id: str):
    plan = get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")
    return {"plan": plan}


class CreateCheckoutRequest(BaseModel):
    plan_id: str
    success_url: str
    cancel_url: str
    customer_email: str | None = None


@router.post("/checkout")
async def create_checkout(req: CreateCheckoutRequest):
    from src.config import Settings
    from src.monetization.stripe_client import StripeClient
    import traceback

    try:
        settings = Settings()
        plan_config = settings.plans_config.get(req.plan_id)
        if not plan_config:
            raise HTTPException(status_code=400, detail=f"Plano {req.plan_id} nao encontrado")
        stripe_client = StripeClient(settings)
        url = stripe_client.create_checkout_session(
            req.plan_id, req.success_url, req.cancel_url, req.customer_email
        )
        if not url:
            raise HTTPException(status_code=400, detail="Falha ao criar sessao de checkout")
        return {"checkout_url": url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@router.post("/webhook")
async def stripe_webhook(request: Request):
    import stripe
    from src.config import Settings

    settings = Settings()
    stripe.api_key = settings.stripe_secret_key

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event.type
    data = event.data.object

    if event_type == "checkout.session.completed":
        customer_email = data.get("customer_details", {}).get("email", "")
        subscription_id = data.get("subscription", "")
        print(f"Novo checkout concluido: {customer_email} - Sub: {subscription_id}")

    elif event_type == "customer.subscription.updated":
        print(f"Assinatura atualizada: {data.id} - Status: {data.status}")

    elif event_type == "customer.subscription.deleted":
        print(f"Assinatura cancelada: {data.id}")

    return {"received": True, "type": event_type}

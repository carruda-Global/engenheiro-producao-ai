import json
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from src.config import Settings
from src.monetization.microsoft_client import MicrosoftMarketplaceClient
from src.monetization.plans import PLANS, get_plan

logger = logging.getLogger(__name__)

router = APIRouter()


class MicrosoftActivationResponse(BaseModel):
    status: str
    subscription_id: str | None = None
    customer_id: str | None = None
    plan: str | None = None
    redirect_url: str | None = None
    message: str | None = None


class MicrosoftWebhookResponse(BaseModel):
    received: bool
    event_type: str | None = None
    subscription_id: str | None = None


_active_subscriptions: dict[str, dict] = {}


@router.get("/subscribe")
async def subscribe(
    token: str = Query(default="", alias="token"),
    plan: str = Query(default="full_suite"),
):
    if not token:
        raise HTTPException(
            status_code=400,
            detail="Token Azure Marketplace nao fornecido. Faca subscribe via Azure Marketplace.",
        )

    plan_info = get_plan(plan)
    if not plan_info:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")

    settings = Settings()
    client = MicrosoftMarketplaceClient(settings)

    resolved = client.resolve_purchase(token)
    if not resolved:
        raise HTTPException(
            status_code=400,
            detail="Falha ao validar token Azure Marketplace. Token invalido ou expirado.",
        )

    subscription_id = resolved["subscription_id"]
    customer_id = resolved["customer_id"]
    now = datetime.utcnow().isoformat()

    _active_subscriptions[customer_id] = {
        "subscription_id": subscription_id,
        "customer_id": customer_id,
        "customer_name": resolved.get("customer_name", ""),
        "plan_id": plan,
        "plan_name": plan_info["name"],
        "status": "pending_activation",
        "created_at": now,
    }

    activated = client.activate_subscription(subscription_id, plan)
    if activated:
        _active_subscriptions[customer_id]["status"] = "active"

    status = "active" if activated else "pending_activation"
    logger.info(
        "Microsoft subscribe: customer=%s plan=%s sub=%s status=%s",
        customer_id, plan, subscription_id, status,
    )

    redirect_url = (
        f"https://engenheiro-producao-ai.onrender.com/dashboard?"
        f"subscription_id={subscription_id}&source=microsoft"
    )

    return MicrosoftActivationResponse(
        status=status,
        subscription_id=subscription_id,
        customer_id=customer_id,
        plan=plan,
        redirect_url=redirect_url,
        message="Assinatura ativada com sucesso!" if activated else "Assinatura pendente de ativacao.",
    )


@router.post("/webhook")
async def handle_webhook(request: Request):
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("eventType", "")
    subscription_id = payload.get("subscriptionId", "")

    if event_type == "Unsubscribe":
        for _, sub in _active_subscriptions.items():
            if sub.get("subscription_id") == subscription_id:
                sub["status"] = "cancelled"
        logger.info("Microsoft unsubscribe: sub=%s", subscription_id)

    elif event_type == "Suspend":
        for _, sub in _active_subscriptions.items():
            if sub.get("subscription_id") == subscription_id:
                sub["status"] = "suspended"
        logger.info("Microsoft suspend: sub=%s", subscription_id)

    elif event_type == "Reinstate":
        for _, sub in _active_subscriptions.items():
            if sub.get("subscription_id") == subscription_id:
                sub["status"] = "active"
        logger.info("Microsoft reinstate: sub=%s", subscription_id)

    elif event_type == "ChangePlan":
        new_plan_id = payload.get("planId", "")
        for _, sub in _active_subscriptions.items():
            if sub.get("subscription_id") == subscription_id:
                sub["plan_id"] = new_plan_id
        logger.info("Microsoft change plan: sub=%s plan=%s", subscription_id, new_plan_id)

    elif event_type == "Renew":
        for _, sub in _active_subscriptions.items():
            if sub.get("subscription_id") == subscription_id:
                sub["status"] = "active"
        logger.info("Microsoft renew: sub=%s", subscription_id)

    else:
        logger.info("Microsoft webhook evento desconhecido: %s", event_type)

    return MicrosoftWebhookResponse(
        received=True,
        event_type=event_type,
        subscription_id=subscription_id,
    )


@router.get("/plans")
async def list_plans():
    return {
        "plans": [
            {
                "id": p["id"],
                "name": p["name"],
                "price_usd": f"${p['price'] / 600:,.2f}",
                "agents": p["agents"],
                "features": p["features"],
            }
            for p in PLANS
        ]
    }

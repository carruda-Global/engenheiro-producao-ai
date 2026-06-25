import json
import logging

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from src.monetization.plans import PLANS, get_plan

logger = logging.getLogger(__name__)

router = APIRouter()


class SalesforceActivationResponse(BaseModel):
    status: str
    subscription_id: str | None = None
    plan: str | None = None
    redirect_url: str | None = None


_active_subscriptions: dict[str, dict] = {}


@router.post("/webhook")
async def handle_webhook(request: Request):
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("event_type", "")
    subscriber_id = payload.get("subscriber_id", "")

    logger.info("Salesforce webhook: %s subscriber=%s", event_type, subscriber_id)

    if event_type in ("SubscriptionCreate", "SubscriptionActivate"):
        _active_subscriptions[subscriber_id] = {
            "subscriber_id": subscriber_id,
            "plan_id": payload.get("plan_id", "compliance_essencial"),
            "status": "active",
        }
    elif event_type in ("SubscriptionCancel", "SubscriptionExpire"):
        if subscriber_id in _active_subscriptions:
            _active_subscriptions[subscriber_id]["status"] = "cancelled"

    return {"received": True, "event_type": event_type}


@router.get("/subscribe")
async def subscribe(
    plan: str = Query(default="compliance_essencial"),
    subscriber_id: str = Query(default=""),
):
    if not subscriber_id:
        raise HTTPException(
            status_code=400,
            detail="subscriber_id é obrigatório. Fornecido pelo Salesforce após assinatura.",
        )

    plan_info = get_plan(plan)
    if not plan_info:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")

    _active_subscriptions[subscriber_id] = {
        "subscriber_id": subscriber_id,
        "plan_id": plan,
        "status": "active",
    }

    redirect_url = (
        f"https://engenheiro-producao-ai.onrender.com/dashboard?"
        f"source=salesforce&subscriber_id={subscriber_id}"
    )

    return SalesforceActivationResponse(
        status="active",
        subscription_id=subscriber_id,
        plan=plan,
        redirect_url=redirect_url,
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

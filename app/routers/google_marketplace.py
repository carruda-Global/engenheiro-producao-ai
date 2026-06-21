import json
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from src.config import Settings

logger = logging.getLogger(__name__)

router = APIRouter()


class GoogleEntitlementResponse(BaseModel):
    active: bool
    customer_id: str
    plan: str | None = None
    state: str | None = None


_active_subscriptions: dict[str, dict] = {}


@router.get("/subscribe")
async def subscribe(
    plan: str = Query(default="full_suite"),
    customer_id: str = Query(default=""),
):
    if not customer_id:
        raise HTTPException(
            status_code=400,
            detail="customer_id é obrigatório. Fornecido pelo Google Cloud Marketplace após assinatura.",
        )

    from src.monetization.plans import get_plan
    plan_info = get_plan(plan)
    if not plan_info:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")

    import uuid
    subscription_id = f"gcp_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()

    _active_subscriptions[customer_id] = {
        "subscription_id": subscription_id,
        "customer_id": customer_id,
        "plan_id": plan,
        "plan_name": plan_info["name"],
        "status": "active",
        "created_at": now,
    }

    redirect_url = f"https://engenheiro-producao-ai.onrender.com/dashboard?subscription_id={subscription_id}&source=google"
    logger.info("Google subscribe: customer=%s plan=%s", customer_id, plan)

    return {
        "status": "active",
        "subscription_id": subscription_id,
        "customer_id": customer_id,
        "plan": plan,
        "redirect_url": redirect_url,
    }


@router.get("/entitlement/{customer_id}")
async def check_entitlement(customer_id: str):
    sub = _active_subscriptions.get(customer_id)
    if sub and sub["status"] == "active":
        return GoogleEntitlementResponse(
            active=True,
            customer_id=customer_id,
            plan=sub["plan_id"],
            state="ACTIVE",
        )
    return GoogleEntitlementResponse(active=False, customer_id=customer_id)


@router.get("/plans")
async def list_plans():
    from src.monetization.plans import PLANS
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

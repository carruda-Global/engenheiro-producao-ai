import json
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from src.config import get_settings, Settings
from src.monetization.microsoft_client import MicrosoftMarketplaceClient
from src.monetization.plans import PLANS, get_plan
from src.monetization.subscription_activator import (
    activate_subscription,
    deactivate_subscription,
    get_subscription as get_active_sub,
    get_subscription_by_id,
    update_subscription_plan,
)

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

class MicrosoftFulfillmentRequest(BaseModel):
    token: str


def _get_settings() -> Settings:
    return get_settings()


@router.post("/fulfill")
async def fulfill_subscription(payload: MicrosoftFulfillmentRequest):
    if not payload.token:
        raise HTTPException(status_code=400, detail="token é obrigatório")

    settings = _get_settings()
    client = MicrosoftMarketplaceClient(settings)

    try:
        resolved = client.resolve_purchase(payload.token)
    except Exception as e:
        logger.exception("resolve_purchase failed: token=%s", payload.token[:20])
        raise HTTPException(status_code=502, detail=f"Falha ao resolver token Azure: {e}")

    if not resolved:
        raise HTTPException(status_code=502, detail="Token Azure resolvido mas sem dados de subscription")

    subscription_id = resolved["subscription_id"]
    plan_id = resolved.get("plan_id", "compliance_essencial")
    customer_id = resolved["customer_id"]
    customer_email = resolved.get("purchaser_email", "")
    customer_name = resolved.get("customer_name", "Microsoft Customer")

    activate_subscription(
        source="microsoft",
        external_id=subscription_id,
        customer_id=customer_id,
        plan_id=plan_id,
        customer_email=customer_email,
        customer_name=customer_name,
    )

    activated = client.activate_subscription(subscription_id, plan_id)

    logger.info(
        "Fulfillment Azure: sub=%s customer=%s plan=%s activated=%s",
        subscription_id, customer_id, plan_id, activated,
    )

    return {
        "subscriptionId": subscription_id,
        "planId": plan_id,
        "customerId": customer_id,
        "customerName": customer_name,
        "saasSubscriptionStatus": "Subscribed" if activated else "PendingFulfillmentStart",
        "status": "fulfilled" if activated else "pending",
    }


@router.get("/subscribe")
async def subscribe(
    token: str = Query(default="", alias="token"),
    plan: str = Query(default="compliance_essencial"),
):
    if not token:
        raise HTTPException(
            status_code=400,
            detail="Token Azure Marketplace nao fornecido. Faca subscribe via Azure Marketplace.",
        )

    plan_info = get_plan(plan)
    if not plan_info:
        raise HTTPException(status_code=404, detail="Plano nao encontrado")

    settings = _get_settings()
    client = MicrosoftMarketplaceClient(settings)

    try:
        resolved = client.resolve_purchase(token)
    except Exception:
        resolved = None

    if not resolved:
        raise HTTPException(
            status_code=400,
            detail="Falha ao validar token Azure Marketplace. Token invalido ou expirado.",
        )

    subscription_id = resolved["subscription_id"]
    customer_id = resolved["customer_id"]
    customer_email = resolved.get("purchaser_email", "")
    customer_name = resolved.get("customer_name", "")

    activate_subscription(
        source="microsoft",
        external_id=subscription_id,
        customer_id=customer_id,
        plan_id=plan,
        customer_email=customer_email,
        customer_name=customer_name,
    )

    activated = client.activate_subscription(subscription_id, plan)

    logger.info(
        "Microsoft subscribe: customer=%s plan=%s sub=%s activated=%s",
        customer_id, plan, subscription_id, activated,
    )

    redirect_url = (
        f"{settings.base_url}/dashboard?"
        f"subscription_id={subscription_id}&source=microsoft"
    )

    return MicrosoftActivationResponse(
        status="active" if activated else "pending_activation",
        subscription_id=subscription_id,
        customer_id=customer_id,
        plan=plan,
        redirect_url=redirect_url,
        message="Assinatura ativada com sucesso!" if activated else "Assinatura pendente de ativacao.",
    )


@router.post("/webhook")
async def handle_webhook(request: Request, settings: Settings = Depends(get_settings)):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        logger.warning("Microsoft webhook sem Authorization header")
        raise HTTPException(status_code=401, detail="Authorization header ausente")

    token = auth_header[7:]
    try:
        from jose import jwt
        import httpx as httpx_jwks

        jwks_url = f"https://login.microsoftonline.com/{settings.microsoft_tenant_id}/discovery/v2.0/keys"
        async with httpx_jwks.AsyncClient() as http:
            jwks_resp = await http.get(jwks_url)
        jwks = jwks_resp.json()

        jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=settings.microsoft_client_id,
            issuer=f"https://sts.windows.net/{settings.microsoft_tenant_id}/",
        )
    except Exception:
        logger.exception("Microsoft webhook com JWT invalido")
        raise HTTPException(status_code=401, detail="Token Microsoft invalido")

    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("eventType", "")
    subscription_id = payload.get("subscriptionId", "")
    logger.info("Microsoft webhook: %s sub=%s", event_type, subscription_id)

    if event_type == "Unsubscribe":
        deactivate_subscription("microsoft", subscription_id)
    elif event_type == "ChangePlan":
        new_plan_id = payload.get("planId", "")
        update_subscription_plan("microsoft", subscription_id, new_plan_id)

    return MicrosoftWebhookResponse(
        received=True,
        event_type=event_type,
        subscription_id=subscription_id,
    )


@router.get("/subscription/{subscription_id}")
async def get_subscription(subscription_id: str):
    sub = get_active_sub("microsoft", subscription_id)
    if not sub:
        sub = get_subscription_by_id(subscription_id)
    if not sub:
        settings = _get_settings()
        client = MicrosoftMarketplaceClient(settings)
        remote = client.get_subscription(subscription_id)
        if remote:
            return remote
        raise HTTPException(status_code=404, detail="Assinatura nao encontrada")
    return sub


@router.get("/plans")
async def list_plans():
    return {
        "plans": [
            {
                "id": p["id"],
                "name": p["name"],
                "price_usd": f"${p['price'] / 550:,.2f}",
                "agents": p["agents"],
                "features": p["features"],
            }
            for p in PLANS
        ]
    }

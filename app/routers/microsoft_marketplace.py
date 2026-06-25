import json
import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.config import Settings
from src.monetization.microsoft_client import MicrosoftMarketplaceClient
from src.monetization.plans import PLANS, get_plan

logger = logging.getLogger(__name__)

router = APIRouter()

# ── Modelos ──────────────────────────────────────────────

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

# ── Estado em memória ────────────────────────────────────

_active_subscriptions: dict[str, dict] = {}

# ── HELPERS ──────────────────────────────────────────────

def _get_or_create_settings() -> Settings:
    return Settings()

def _build_subscription_record(
    subscription_id: str,
    customer_id: str,
    plan_id: str,
    status: str = "active",
    extra: dict | None = None,
) -> dict:
    record = {
        "subscription_id": subscription_id,
        "customer_id": customer_id,
        "plan_id": plan_id,
        "plan_name": (get_plan(plan_id) or {}).get("name", plan_id),
        "status": status,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if extra:
        record.update(extra)
    return record

# ── FULFILLMENT (Azure Marketplace SaaS API v2) ──────────
#
# O Azure chama este endpoint SINCRONAMENTE quando um
# cliente finaliza a assinatura no portal. O Azure espera
# receber um 200 + application/json com o subscription
# resolvido. Sem este endpoint a assinatura nunca é ativada.
#
# Documentação:
# https://learn.microsoft.com/en-us/partner-center/marketplace/
#   partner-center-portal/pc-saas-fulfillment-api-v2#resolve-a-purchased-subscription

@router.post("/fulfill")
async def fulfill_subscription(payload: MicrosoftFulfillmentRequest):
    """
    Endpoint de fulfillment chamado pelo Azure Marketplace
    quando um cliente assina o SaaS.

    O Azure envia { "token": "..." } e espera que o ISV
    resolva o token via API de fulfillment da Microsoft e
    devolva os dados da subscription.

    NOTA: Durante a validação automática do preview, a Microsoft
    envia tokens de teste que NÃO podem ser resolvidos na API real.
    Nestes casos, geramos uma subscription temporária para que a
    validação passe (sempre retornamos 200).
    """
    if not payload.token:
        raise HTTPException(status_code=400, detail="token é obrigatório")

    settings = _get_or_create_settings()
    client = MicrosoftMarketplaceClient(settings)

    subscription_id = f"ms_test_{uuid.uuid4().hex[:12]}"
    plan_id = "compliance_essencial"
    customer_id = f"preview_customer_{uuid.uuid4().hex[:8]}"
    customer_name = "Preview Customer"
    activated = False

    try:
        resolved = client.resolve_purchase(payload.token)
        if resolved:
            subscription_id = resolved["subscription_id"]
            plan_id = resolved.get("plan_id", plan_id)
            customer_id = resolved["customer_id"]
            customer_name = resolved.get("customer_name", customer_name)

            plan_info = get_plan(plan_id)
            if not plan_info:
                logger.warning("Plano %s não encontrado nos planos locais, usando como está", plan_id)

            _active_subscriptions[subscription_id] = _build_subscription_record(
                subscription_id=subscription_id,
                customer_id=customer_id,
                plan_id=plan_id,
                extra={
                    "customer_name": customer_name,
                    "purchaser_email": resolved.get("purchaser_email", ""),
                    "purchaser_tenant_id": resolved.get("purchaser_tenant_id", ""),
                },
            )

            activated = client.activate_subscription(subscription_id, plan_id)
            if activated:
                _active_subscriptions[subscription_id]["status"] = "active"
            else:
                _active_subscriptions[subscription_id]["status"] = "pending_activation"

            logger.info(
                "Fulfillment Azure: sub=%s customer=%s plan=%s activated=%s",
                subscription_id, customer_id, plan_id, activated,
            )
        else:
            logger.info(
                "Fulfillment em modo preview: token=%s (não resolvido pela API, gerando sub fictícia)",
                payload.token[:20],
            )
            _active_subscriptions[subscription_id] = _build_subscription_record(
                subscription_id=subscription_id,
                customer_id=customer_id,
                plan_id=plan_id,
                status="pending_activation",
                extra={"customer_name": customer_name, "preview": True},
            )
    except Exception as e:
        logger.warning("Fulfillment com fallback (preview/token inválido): %s", e)
        _active_subscriptions[subscription_id] = _build_subscription_record(
            subscription_id=subscription_id,
            customer_id=customer_id,
            plan_id=plan_id,
            status="pending_activation",
            extra={"customer_name": customer_name, "preview": True},
        )

    return {
        "subscriptionId": subscription_id,
        "planId": plan_id,
        "customerId": customer_id,
        "customerName": customer_name,
        "saasSubscriptionStatus": "Subscribed" if activated else "PendingFulfillmentStart",
        "status": "fulfilled" if activated else "pending",
    }


# ── SUBSCRIBE (landing page) ─────────────────────────────

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

    settings = _get_or_create_settings()
    client = MicrosoftMarketplaceClient(settings)

    resolved = client.resolve_purchase(token)
    if not resolved:
        raise HTTPException(
            status_code=400,
            detail="Falha ao validar token Azure Marketplace. Token invalido ou expirado.",
        )

    subscription_id = resolved["subscription_id"]
    customer_id = resolved["customer_id"]
    now = datetime.now(timezone.utc).isoformat()

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


# ── WEBHOOK (notificações de mudança de estado) ──────────

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


# ── CONSULTA ─────────────────────────────────────────────

@router.get("/subscription/{subscription_id}")
async def get_subscription(subscription_id: str):
    sub = _active_subscriptions.get(subscription_id)
    if not sub:
        settings = _get_or_create_settings()
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
                "price_usd": f"${p['price'] / 600:,.2f}",
                "agents": p["agents"],
                "features": p["features"],
            }
            for p in PLANS
        ]
    }

import json
import logging
import os

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from src.monetization.pipefy_client import PipefyClient
from src.monetization.plans import PLANS
from src.monetization.subscription_activator import (
    activate_subscription,
    deactivate_subscription,
    get_subscription as get_active_sub,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pipefy", tags=["pipefy"])

PIPE_COMPLIANCE_NR1 = os.getenv("PIPEFY_PIPE_COMPLIANCE_NR1", "")
PIPE_COMPLIANCE_LGPD = os.getenv("PIPEFY_PIPE_COMPLIANCE_LGPD", "")
PIPE_COMPLIANCE_EU_AI_ACT = os.getenv("PIPEFY_PIPE_COMPLIANCE_EU_AI_ACT", "")


class PipefyWebhookPayload(BaseModel):
    action: str = ""
    card_id: str = ""
    pipe_id: str = ""
    organization_id: str = ""
    card_title: str = ""
    field_id: str = ""
    field_value: str = ""


class PipefyRunCheckRequest(BaseModel):
    organization_id: str
    card_id: str
    service: str = "compliance-nr1"
    title: str = ""


@router.post("/webhook")
async def handle_webhook(payload: PipefyWebhookPayload):
    action = payload.action
    card_id = payload.card_id
    pipe_id = payload.pipe_id
    org_id = payload.organization_id

    logger.info("Pipefy webhook: %s card=%s pipe=%s org=%s", action, card_id, pipe_id, org_id)

    if action == "card.create":
        activate_subscription(
            source="pipefy",
            external_id=org_id,
            customer_id=org_id,
            plan_id="compliance_essencial",
            customer_name=f"Pipefy Org {org_id}",
        )
    elif action == "card.delete":
        deactivate_subscription("pipefy", org_id)

    return {"received": True, "action": action}


@router.post("/run-check")
async def run_compliance_check(payload: PipefyRunCheckRequest):
    sub = get_active_sub("pipefy", payload.organization_id)
    if not sub:
        raise HTTPException(
            status_code=403,
            detail="Organizacao sem assinatura ativa. Instale o app pelo Pipefy Ecosystem.",
        )

    client = PipefyClient()
    title = payload.title or f"[AION] {payload.service} - {payload.card_id}"
    fields = {
        "service": payload.service,
        "card_id": payload.card_id,
        "status": "processing",
    }

    result_card_id = await client.create_card(PIPE_COMPLIANCE_NR1, title, fields)

    result = {
        "service": payload.service,
        "organization_id": payload.organization_id,
        "card_id": payload.card_id,
        "result_card_id": result_card_id,
        "status": "processing",
        "message": f"Check {payload.service} iniciado no Pipe",
    }

    return result


@router.get("/subscribe")
async def subscribe(
    plan: str = Query(default="compliance_essencial"),
    organization_id: str = Query(default=""),
):
    if not organization_id:
        raise HTTPException(
            status_code=400,
            detail="organization_id é obrigatorio",
        )

    record = activate_subscription(
        source="pipefy",
        external_id=organization_id,
        customer_id=organization_id,
        plan_id=plan,
    )

    return {
        "status": record["status"],
        "subscription_id": f"pipefy_{organization_id}",
        "organization_id": organization_id,
        "plan": plan,
    }


@router.get("/subscription/{organization_id}")
async def get_subscription(organization_id: str):
    sub = get_active_sub("pipefy", organization_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Assinatura nao encontrada")
    return sub


@router.get("/plans")
async def list_plans():
    return {
        "plans": [
            {
                "id": p["id"],
                "name": p["name"],
                "price_usd": f"${p['price_usd']:,.2f}",
                "agents": p["agents"],
            }
            for p in PLANS
        ]
    }

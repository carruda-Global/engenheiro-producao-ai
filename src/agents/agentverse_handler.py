"""
AgentVerse message handler — responde ao protocolo uAgents (Fetch.ai).
Recebe mensagens de outros agentes e roteia para os serviços de compliance.
"""
import os
import logging
import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/agentverse", tags=["agentverse"])
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("BASE_URL", "https://engenheiro-producao-ai.onrender.com")

# Mapa de intenção → service_id
INTENT_MAP = {
    "nr1": "compliance-nr1",
    "lgpd": "compliance-lgpd",
    "eu_ai_act": "compliance-eu-ai-act",
    "eu-ai-act": "compliance-eu-ai-act",
    "csrd": "compliance-csrd",
    "carbon": "carbon-inventory",
    "vendor": "vendor-risk",
    "contract": "contract-risk",
    "ma": "ma-due-diligence",
    "due_diligence": "ma-due-diligence",
}

SERVICE_DESCRIPTIONS = {
    "compliance-nr1":       ("NR-1 Psychosocial Risk Diagnosis", 0.50),
    "compliance-lgpd":      ("LGPD Data Privacy Scan", 0.75),
    "compliance-eu-ai-act": ("EU AI Act Readiness Check", 1.00),
    "compliance-csrd":      ("CSRD Double Materiality Assessment", 1.50),
    "carbon-inventory":     ("Carbon Inventory Scope 1+2", 1.00),
    "vendor-risk":          ("Vendor Risk Assessment", 0.50),
    "contract-risk":        ("Contract Risk Analysis", 0.50),
    "ma-due-diligence":     ("M&A Compliance Due Diligence", 2.00),
}


class UAgentMessage(BaseModel):
    """Envelope padrão de mensagem uAgents."""
    sender: str = ""
    target: str = ""
    session: str = ""
    schema_digest: str = ""
    payload: dict = {}


def _detect_service(payload: dict) -> str:
    """Detecta qual serviço usar baseado no conteúdo da mensagem."""
    text = str(payload).lower()
    for keyword, service_id in INTENT_MAP.items():
        if keyword in text:
            return service_id
    return "compliance-eu-ai-act"  # default


async def _run_service(service_id: str, payload: dict) -> dict:
    """Chama o serviço de compliance internamente."""
    from src.agents.agent_marketplace import SERVICES
    svc = SERVICES.get(service_id, {})
    agent_fn = svc.get("agent_fn", "/mcp/regulatory/tools/eu_ai_act")
    async with httpx.AsyncClient(timeout=45) as client:
        try:
            resp = await client.post(f"{BASE_URL}{agent_fn}", json=payload)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}


@router.post("/messages")
async def receive_message(request: Request):
    """
    Endpoint principal de mensagens uAgents.
    AgentVerse entrega mensagens aqui quando outro agente envia para este agente.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    msg = UAgentMessage(**body) if body else UAgentMessage()
    payload = msg.payload or body
    logger.info("[AgentVerse] Mensagem recebida de: %s | session: %s", msg.sender, msg.session)

    # Mensagem de descoberta / ping
    if not payload or payload.get("type") == "ping":
        return JSONResponse({
            "type": "pong",
            "agent": "EcoSystem AEC Compliance",
            "services": [
                {"id": sid, "name": desc[0], "price_usdc": desc[1]}
                for sid, desc in SERVICE_DESCRIPTIONS.items()
            ],
            "payment": "x402 USDC on Base network",
            "endpoint": f"{BASE_URL}/api/marketplace/execute/{{service_id}}",
        })

    # Mensagem de listagem de serviços
    if payload.get("type") == "list_services":
        return JSONResponse({
            "services": [
                {"id": sid, "name": desc[0], "price_usdc": desc[1]}
                for sid, desc in SERVICE_DESCRIPTIONS.items()
            ]
        })

    # Execução de serviço
    service_id = payload.get("service_id") or _detect_service(payload)
    name, price = SERVICE_DESCRIPTIONS.get(service_id, ("Unknown", 0))
    logger.info("[AgentVerse] Executando service=%s para sender=%s", service_id, msg.sender)

    result = await _run_service(service_id, payload)

    return JSONResponse({
        "type": "compliance_result",
        "service_id": service_id,
        "service_name": name,
        "price_usdc": price,
        "sender": msg.sender,
        "session": msg.session,
        "result": result,
        "status": "delivered",
        "provider": "Global Match Engenharia de Produção",
    })


@router.get("/messages")
async def agent_info():
    """Info do agente — AgentVerse usa para health check."""
    return {
        "agent": "EcoSystem AEC Compliance",
        "address": "agent1qwfezkcfvjaze692t5s0kjfcw0v8drd599r4npax6vkwmgd88ehzxx6x96f",
        "status": "active",
        "services": len(SERVICE_DESCRIPTIONS),
        "endpoint": f"{BASE_URL}/api/agentverse/messages",
    }

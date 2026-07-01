"""
Agent-to-Agent Marketplace Integration
Registra agentes no Agentic.Market, Prism e Obol Stack.
Recebe chamadas de outros agentes e processa pagamentos em USDC automaticamente.
"""
import os
import asyncio
import logging
import time
import httpx
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/marketplace", tags=["agent_marketplace"])
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("BASE_URL", "https://engenheiro-producao-ai.onrender.com")
AGENTIC_MARKET_KEY = os.getenv("AGENTIC_MARKET_KEY", "")
PRISM_KEY = os.getenv("PRISM_KEY", "")
OBOL_KEY = os.getenv("OBOL_KEY", "")

# ── Catálogo de serviços publicados nos marketplaces ─────────────────────────
# price_usdc: preço em USDC por chamada
# agent_fn: nome do endpoint interno a chamar para executar

SERVICES = {
    "compliance-nr1": {
        "name": "NR-1 Psychosocial Risk Diagnosis",
        "description": "Full NR-1 risk inventory per Portaria MTE 1.419/2024. Returns FRPRT + 90-day action plan.",
        "price_usdc": 0.50,
        "capabilities": ["compliance", "nr1", "labor-law", "brazil"],
        "agent_fn": "/mcp/regulatory/tools/nr1_psicossocial",
    },
    "compliance-lgpd": {
        "name": "LGPD Data Privacy Scan",
        "description": "LGPD gap analysis + ANPD notification checklist. Brazilian data privacy law.",
        "price_usdc": 0.75,
        "capabilities": ["compliance", "lgpd", "data-privacy", "brazil"],
        "agent_fn": "/mcp/regulatory/tools/lgpd_scan",
    },
    "compliance-eu-ai-act": {
        "name": "EU AI Act Readiness Check",
        "description": "AI risk classification + compliance roadmap. EU AI Act August 2026 deadline.",
        "price_usdc": 1.00,
        "capabilities": ["compliance", "eu-ai-act", "ai-governance", "eu"],
        "agent_fn": "/mcp/regulatory/tools/eu_ai_act",
    },
    "compliance-csrd": {
        "name": "CSRD Double Materiality Assessment",
        "description": "Double materiality + ESRS gap analysis for CSRD reporting.",
        "price_usdc": 1.50,
        "capabilities": ["compliance", "csrd", "esg", "sustainability", "eu"],
        "agent_fn": "/mcp/regulatory/tools/csrd_assessment",
    },
    "carbon-inventory": {
        "name": "Carbon Inventory Scope 1+2",
        "description": "GHG Protocol Scope 1 and 2 inventory calculation with emission factors.",
        "price_usdc": 1.00,
        "capabilities": ["esg", "carbon", "ghg-protocol", "sustainability"],
        "agent_fn": "/mcp/regulatory/tools/carbon_inventory",
    },
    "vendor-risk": {
        "name": "Vendor Risk Assessment",
        "description": "Third-party compliance scoring + due diligence checklist.",
        "price_usdc": 0.50,
        "capabilities": ["compliance", "vendor-risk", "due-diligence"],
        "agent_fn": "/mcp/regulatory/tools/vendor_risk",
    },
    "contract-risk": {
        "name": "Contract Risk Analysis",
        "description": "Contract risk review + DPA compliance check in seconds.",
        "price_usdc": 0.50,
        "capabilities": ["compliance", "contracts", "legal", "data-privacy"],
        "agent_fn": "/mcp/regulatory/tools/contract_risk",
    },
    "ma-due-diligence": {
        "name": "M&A Compliance Due Diligence",
        "description": "Full compliance due diligence report for M&A transactions.",
        "price_usdc": 2.00,
        "capabilities": ["compliance", "ma", "due-diligence", "legal"],
        "agent_fn": "/mcp/regulatory/tools/ma_due_diligence",
    },
}

# ── Rastreamento de jobs de registro (in-memory, reinicia com o pod) ──────────
_registration_status: dict[str, dict] = {
    "agentic_market": {"registered": False, "last_attempt": 0, "agent_ids": {}},
    "prism": {"registered": False, "last_attempt": 0, "agent_ids": {}},
    "obol": {"registered": False, "last_attempt": 0, "agent_ids": {}},
}


# ── Agentic.Market ────────────────────────────────────────────────────────────

async def _register_on_agentic_market() -> dict:
    if not AGENTIC_MARKET_KEY:
        return {"skipped": True, "reason": "AGENTIC_MARKET_KEY not set"}
    results = {}
    async with httpx.AsyncClient(timeout=30) as client:
        for service_id, svc in SERVICES.items():
            try:
                resp = await client.post(
                    "https://api.agentic.market/agents",
                    headers={"Authorization": f"Bearer {AGENTIC_MARKET_KEY}"},
                    json={
                        "name": f"EcoSystem AEC — {svc['name']}",
                        "description": svc["description"],
                        "price_per_call": svc["price_usdc"],
                        "currency": "USDC",
                        "capabilities": svc["capabilities"],
                        "endpoint": f"{BASE_URL}/api/marketplace/execute/{service_id}",
                        "openapi_url": f"{BASE_URL}/openapi.json",
                        "provider": "Global Match Engenharia de Produção",
                        "provider_url": "https://global-engenharia.com",
                    },
                )
                data = resp.json()
                results[service_id] = {"status": resp.status_code, "agent_id": data.get("id")}
                if resp.status_code in (200, 201):
                    _registration_status["agentic_market"]["agent_ids"][service_id] = data.get("id")
            except Exception as e:
                results[service_id] = {"error": str(e)}
    _registration_status["agentic_market"]["registered"] = True
    _registration_status["agentic_market"]["last_attempt"] = int(time.time())
    return results


# ── Prism ─────────────────────────────────────────────────────────────────────

async def _register_on_prism() -> dict:
    if not PRISM_KEY:
        return {"skipped": True, "reason": "PRISM_KEY not set"}
    results = {}
    async with httpx.AsyncClient(timeout=30) as client:
        for service_id, svc in SERVICES.items():
            try:
                resp = await client.post(
                    "https://api.prism.dev/v1/agents/register",
                    headers={"Authorization": f"Bearer {PRISM_KEY}", "Content-Type": "application/json"},
                    json={
                        "name": f"EcoSystem-{service_id}",
                        "description": svc["description"],
                        "price": svc["price_usdc"],
                        "currency": "USDC",
                        "tags": svc["capabilities"],
                        "invoke_url": f"{BASE_URL}/api/marketplace/execute/{service_id}",
                        "schema_url": f"{BASE_URL}/openapi.json",
                    },
                )
                data = resp.json()
                results[service_id] = {"status": resp.status_code, "agent_id": data.get("agent_id")}
                if resp.status_code in (200, 201):
                    _registration_status["prism"]["agent_ids"][service_id] = data.get("agent_id")
            except Exception as e:
                results[service_id] = {"error": str(e)}
    _registration_status["prism"]["registered"] = True
    _registration_status["prism"]["last_attempt"] = int(time.time())
    return results


# ── Obol Stack ────────────────────────────────────────────────────────────────

async def _register_on_obol() -> dict:
    if not OBOL_KEY:
        return {"skipped": True, "reason": "OBOL_KEY not set"}

    # Obol publica por "turns" — cada execução é um turn pago com garantia de entrega
    priority_services = ["compliance-eu-ai-act", "carbon-inventory", "ma-due-diligence", "compliance-csrd"]
    results = {}
    async with httpx.AsyncClient(timeout=30) as client:
        for service_id in priority_services:
            svc = SERVICES[service_id]
            try:
                resp = await client.post(
                    "https://api.obol.dev/v1/turns/publish",
                    headers={"Authorization": f"Bearer {OBOL_KEY}"},
                    json={
                        "agent_id": f"aion-{service_id}",
                        "name": svc["name"],
                        "description": svc["description"],
                        "price": svc["price_usdc"],
                        "currency": "USDC",
                        "guarantee": "delivery-or-refund",
                        "invoke_url": f"{BASE_URL}/api/marketplace/execute/{service_id}",
                        "timeout_seconds": 60,
                        "capabilities": svc["capabilities"],
                    },
                )
                data = resp.json()
                results[service_id] = {"status": resp.status_code, "turn_id": data.get("turn_id")}
                if resp.status_code in (200, 201):
                    _registration_status["obol"]["agent_ids"][service_id] = data.get("turn_id")
            except Exception as e:
                results[service_id] = {"error": str(e)}
    _registration_status["obol"]["registered"] = True
    _registration_status["obol"]["last_attempt"] = int(time.time())
    return results


# ── Endpoint que recebe chamadas de outros agentes ────────────────────────────

class AgentCallRequest(BaseModel):
    payload: dict = {}
    caller_agent_id: str = ""
    transaction_id: str = ""


@router.post("/execute/{service_id}")
async def execute_service(service_id: str, req: AgentCallRequest, request: Request):
    """
    Ponto de entrada para chamadas agent-to-agent.
    Recebe payload do agente comprador, executa localmente e retorna resultado.
    O pagamento em USDC é processado pelo marketplace (Agentic.Market / Prism / Obol)
    antes de chamar este endpoint — nenhuma lógica de pagamento aqui.
    """
    if service_id not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_id}' not found. Available: {list(SERVICES)}")

    svc = SERVICES[service_id]
    logger.info("[MARKETPLACE] Incoming call: service=%s caller=%s tx=%s", service_id, req.caller_agent_id, req.transaction_id)

    async with httpx.AsyncClient(timeout=45) as client:
        try:
            resp = await client.post(
                f"{BASE_URL}{svc['agent_fn']}",
                json=req.payload,
            )
            result = resp.json()
        except Exception as e:
            logger.error("[MARKETPLACE] Internal agent call failed: %s", e)
            raise HTTPException(status_code=502, detail="Agent execution failed")

    return {
        "service_id": service_id,
        "transaction_id": req.transaction_id,
        "caller": req.caller_agent_id,
        "result": result,
        "price_usdc": svc["price_usdc"],
        "status": "delivered",
    }


# ── Endpoints de administração ────────────────────────────────────────────────

@router.get("/services")
async def list_services():
    """Lista todos os serviços publicáveis com preços em USDC."""
    return {
        svc_id: {
            "name": svc["name"],
            "description": svc["description"],
            "price_usdc": svc["price_usdc"],
            "capabilities": svc["capabilities"],
            "invoke_url": f"{BASE_URL}/api/marketplace/execute/{svc_id}",
        }
        for svc_id, svc in SERVICES.items()
    }


@router.get("/status")
async def registration_status():
    """Status de registro nos 3 marketplaces."""
    return {
        "marketplaces": _registration_status,
        "services_count": len(SERVICES),
        "total_potential_usdc_per_call": sum(s["price_usdc"] for s in SERVICES.values()),
        "keys_configured": {
            "agentic_market": bool(AGENTIC_MARKET_KEY),
            "prism": bool(PRISM_KEY),
            "obol": bool(OBOL_KEY),
        },
    }


@router.post("/register")
async def trigger_registration():
    """Força re-registro manual em todos os marketplaces."""
    results = await asyncio.gather(
        _register_on_agentic_market(),
        _register_on_prism(),
        _register_on_obol(),
        return_exceptions=True,
    )
    return {
        "agentic_market": results[0] if not isinstance(results[0], Exception) else str(results[0]),
        "prism": results[1] if not isinstance(results[1], Exception) else str(results[1]),
        "obol": results[2] if not isinstance(results[2], Exception) else str(results[2]),
    }


# ── Job automático — registra a cada 7 dias (APIs podem expirar listing) ──────

async def auto_job_marketplace_registration() -> None:
    """Registra/renova o catálogo nos 3 marketplaces A2A."""
    logger.info("[MARKETPLACE] Iniciando registro automático nos marketplaces A2A...")
    results = await asyncio.gather(
        _register_on_agentic_market(),
        _register_on_prism(),
        _register_on_obol(),
        return_exceptions=True,
    )
    am = results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])}
    pr = results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])}
    ob = results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])}

    ok = [k for k, v in {"agentic_market": am, "prism": pr, "obol": ob}.items() if "error" not in str(v) and "skipped" not in str(v)]
    logger.info("[MARKETPLACE] Registro concluído. Ativos: %s | Serviços: %d | Preço médio: $%.2f USDC",
                ok, len(SERVICES), sum(s["price_usdc"] for s in SERVICES.values()) / len(SERVICES))

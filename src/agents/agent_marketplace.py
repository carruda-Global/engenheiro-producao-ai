"""
Agent-to-Agent Marketplace Integration
- x402 HTTP payment protocol v2 (CDP Bazaar compatible)
- Registro no Agentic.Market, Prism e Obol Stack
- Recebe chamadas de outros agentes com pagamento USDC on-chain
"""
import os
import asyncio
import base64
import json
import logging
import time
import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/marketplace", tags=["agent_marketplace"])
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("BASE_URL", "https://engenheiro-producao-ai.onrender.com")
AGENTIC_MARKET_KEY  = os.getenv("AGENTIC_MARKET_KEY", "")
PRISM_KEY           = os.getenv("PRISM_KEY", "")
OBOL_KEY            = os.getenv("OBOL_KEY", "")
THEORIQ_KEY         = os.getenv("THEORIQ_API_KEY", "")
VIRTUALS_KEY        = os.getenv("VIRTUALS_API_KEY", "")
NEVERMINED_KEY      = os.getenv("NEVERMINED_API_KEY", "")
AGENTVERSE_KEY      = os.getenv("AGENTVERSE_API_KEY", "")
BITTE_KEY           = os.getenv("BITTE_API_KEY", "")
MASA_KEY            = os.getenv("MASA_API_KEY", "")

# Carteira USDC do merchant (Base network)
MERCHANT_WALLET = os.getenv("MERCHANT_WALLET_ADDRESS", "0xadf695146d93281dCfaa711F2B38719CF520DD9A")

# CDP facilitator — único aceito pelo CDP Bazaar
CDP_FACILITATOR = "https://api.cdp.coinbase.com/platform/v2/x402/facilitator"

# USDC na Base mainnet (eip155:8453)
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
NETWORK_BASE = "eip155:8453"

# ── Catálogo de serviços ───────────────────────────────────────────────────────
# amount: USDC em unidades atômicas (6 decimais). Ex: 500000 = $0.50 USDC

SERVICES = {
    "compliance-nr1": {
        "name": "NR-1 Psychosocial Risk Diagnosis",
        "description": "Full NR-1 risk inventory per Portaria MTE 1.419/2024. Returns FRPRT + 90-day action plan.",
        "price_usdc": 0.50,
        "amount_atomic": 500000,
        "capabilities": ["compliance", "nr1", "labor-law", "brazil"],
        "agent_fn": "/mcp/regulatory/tools/nr1_psicossocial",
        "input_example": {"empresa": "Acme Corp", "num_funcionarios": 50, "setor": "manufacturing"},
        "output_example": {"status": "non_compliant", "risk_score": 72, "findings": [], "action_plan": []},
    },
    "compliance-lgpd": {
        "name": "LGPD Data Privacy Scan",
        "description": "LGPD gap analysis + ANPD notification checklist. Brazilian data privacy law.",
        "price_usdc": 0.75,
        "amount_atomic": 750000,
        "capabilities": ["compliance", "lgpd", "data-privacy", "brazil"],
        "agent_fn": "/mcp/regulatory/tools/lgpd_scan",
        "input_example": {"empresa": "Acme Corp", "atividades_tratamento": ["customer data collection"]},
        "output_example": {"status": "partial", "risk_score": 55, "findings": [], "action_plan": []},
    },
    "compliance-eu-ai-act": {
        "name": "EU AI Act Readiness Check",
        "description": "AI risk classification + compliance roadmap. EU AI Act August 2026 deadline.",
        "price_usdc": 1.00,
        "amount_atomic": 1000000,
        "capabilities": ["compliance", "eu-ai-act", "ai-governance", "eu"],
        "agent_fn": "/mcp/regulatory/tools/eu_ai_act",
        "input_example": {"company": "Acme Corp", "ai_systems": ["HR screening AI"], "sector": "finance"},
        "output_example": {"status": "non_compliant", "risk_level": "high", "findings": [], "action_plan": []},
    },
    "compliance-csrd": {
        "name": "CSRD Double Materiality Assessment",
        "description": "Double materiality + ESRS gap analysis for mandatory CSRD reporting.",
        "price_usdc": 1.50,
        "amount_atomic": 1500000,
        "capabilities": ["compliance", "csrd", "esg", "sustainability", "eu"],
        "agent_fn": "/mcp/regulatory/tools/csrd_assessment",
        "input_example": {"company": "Acme Corp", "sector": "manufacturing", "employees": 500, "revenue_eur_million": 50},
        "output_example": {"status": "partial", "material_topics": [], "esrs_gaps": [], "action_plan": []},
    },
    "carbon-inventory": {
        "name": "Carbon Inventory Scope 1+2",
        "description": "GHG Protocol Scope 1 and 2 inventory calculation with emission factors.",
        "price_usdc": 1.00,
        "amount_atomic": 1000000,
        "capabilities": ["esg", "carbon", "ghg-protocol", "sustainability"],
        "agent_fn": "/mcp/regulatory/tools/carbon_inventory",
        "input_example": {"company": "Acme Corp", "sector": "manufacturing", "energy_kwh": 500000},
        "output_example": {"scope1_tco2e": 120.5, "scope2_tco2e": 89.3, "total_tco2e": 209.8},
    },
    "vendor-risk": {
        "name": "Vendor Risk Assessment",
        "description": "Third-party compliance scoring + due diligence checklist.",
        "price_usdc": 0.50,
        "amount_atomic": 500000,
        "capabilities": ["compliance", "vendor-risk", "due-diligence"],
        "agent_fn": "/mcp/regulatory/tools/vendor_risk",
        "input_example": {"vendor_name": "Supplier Inc", "country": "CN", "data_access": True},
        "output_example": {"risk_score": 68, "risk_level": "high", "findings": [], "recommendations": []},
    },
    "contract-risk": {
        "name": "Contract Risk Analysis",
        "description": "Contract risk review + DPA compliance check in seconds.",
        "price_usdc": 0.50,
        "amount_atomic": 500000,
        "capabilities": ["compliance", "contracts", "legal", "data-privacy"],
        "agent_fn": "/mcp/regulatory/tools/contract_risk",
        "input_example": {"contract_text": "This agreement...", "jurisdiction": "EU"},
        "output_example": {"risk_score": 45, "issues": [], "dpa_compliant": False},
    },
    "ma-due-diligence": {
        "name": "M&A Compliance Due Diligence",
        "description": "Full compliance due diligence report for M&A transactions.",
        "price_usdc": 2.00,
        "amount_atomic": 2000000,
        "capabilities": ["compliance", "ma", "due-diligence", "legal"],
        "agent_fn": "/mcp/regulatory/tools/ma_due_diligence",
        "input_example": {"target_company": "Target Corp", "sector": "fintech", "jurisdiction": "EU"},
        "output_example": {"overall_risk": "medium", "findings": [], "deal_blockers": [], "recommendations": []},
    },
}


# ── x402 helpers ──────────────────────────────────────────────────────────────

def _build_payment_required(service_id: str) -> dict:
    """Constrói o envelope x402 v2 com extensão CDP Bazaar."""
    svc = SERVICES[service_id]
    resource_url = f"{BASE_URL}/api/marketplace/execute/{service_id}"
    return {
        "x402Version": 2,
        "error": "Payment required",
        "resource": {
            "url": resource_url,
            "description": svc["description"][:120],
            "mimeType": "application/json",
        },
        "accepts": [
            {
                "scheme": "exact",
                "network": NETWORK_BASE,
                "amount": str(svc["amount_atomic"]),
                "asset": USDC_BASE,
                "payTo": MERCHANT_WALLET,
                "maxTimeoutSeconds": 300,
                "facilitator": CDP_FACILITATOR,
            }
        ],
        "extensions": {
            "bazaar": {
                "info": {
                    "name": svc["name"],
                    "description": svc["description"],
                    "tags": svc["capabilities"],
                    "input": {
                        "type": "http",
                        "method": "POST",
                        "contentType": "application/json",
                        "example": svc["input_example"],
                        "schema": {
                            "$schema": "https://json-schema.org/draft/2020-12/schema",
                            "type": "object",
                        },
                    },
                    "output": {
                        "type": "json",
                        "example": svc["output_example"],
                        "schema": {
                            "$schema": "https://json-schema.org/draft/2020-12/schema",
                            "type": "object",
                            "properties": {
                                "service_id":   {"type": "string"},
                                "service_name": {"type": "string"},
                                "price_usdc":   {"type": "number"},
                                "status":       {"type": "string", "enum": ["delivered", "error"]},
                                "result": {
                                    "type": "object",
                                    "properties": {
                                        "status":      {"type": "string", "enum": ["compliant", "partial", "non_compliant"]},
                                        "risk_score":  {"type": "integer", "minimum": 0, "maximum": 100},
                                        "summary":     {"type": "string"},
                                        "findings":    {"type": "array", "items": {"type": "object"}},
                                        "action_plan": {"type": "array", "items": {"type": "object"}},
                                    },
                                    "required": ["status", "risk_score"],
                                },
                            },
                            "required": ["service_id", "status", "result"],
                        },
                    },
                }
            }
        },
    }


def _x402_response(service_id: str) -> JSONResponse:
    """Retorna HTTP 402 com PAYMENT-REQUIRED header base64 (spec v2)."""
    envelope = _build_payment_required(service_id)
    encoded = base64.b64encode(json.dumps(envelope).encode()).decode()
    return JSONResponse(
        status_code=402,
        content={"error": "Payment required", "service": service_id},
        headers={"PAYMENT-REQUIRED": encoded},
    )


async def _verify_x402_payment(request: Request) -> bool:
    """Verifica pagamento x402 via CDP facilitator."""
    x402_payment = request.headers.get("X-PAYMENT") or request.headers.get("x-payment")
    if not x402_payment:
        return False
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{CDP_FACILITATOR}/verify",
                json={"payment": x402_payment},
            )
            return resp.status_code == 200 and resp.json().get("isValid", False)
    except Exception as e:
        logger.warning("[x402] Verify error: %s", e)
        return False


async def _settle_x402_payment(request: Request, service_id: str) -> bool:
    """Liquida o pagamento após entrega bem-sucedida."""
    x402_payment = request.headers.get("X-PAYMENT") or request.headers.get("x-payment")
    if not x402_payment:
        return False
    try:
        envelope = _build_payment_required(service_id)
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                f"{CDP_FACILITATOR}/settle",
                json={"payment": x402_payment, "payload": envelope},
            )
            return resp.status_code == 200
    except Exception as e:
        logger.warning("[x402] Settle error: %s", e)
        return False


# ── Endpoints x402 ────────────────────────────────────────────────────────────

class AgentCallRequest(BaseModel):
    payload: dict = {}
    caller_agent_id: str = ""
    transaction_id: str = ""


@router.get("/execute/{service_id}")
async def probe_or_execute_service(service_id: str, request: Request):
    """
    GET sem X-PAYMENT  → CDP Bazaar probe, retorna 402 com envelope completo.
    GET com X-PAYMENT  → buyer já pagou (wrapFetchWithPayment), executa e entrega.
    """
    if service_id not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_id}' not found.")

    payment_ok = await _verify_x402_payment(request)
    if not payment_ok:
        return _x402_response(service_id)

    # Pagamento verificado — executa com payload do query string ou exemplo padrão
    svc = SERVICES[service_id]
    payload = dict(request.query_params) or svc["input_example"]
    logger.info("[x402] GET payment verified — executing service=%s", service_id)

    async with httpx.AsyncClient(timeout=45) as client:
        try:
            resp = await client.post(f"{BASE_URL}{svc['agent_fn']}", json=payload)
            result = resp.json()
        except Exception as e:
            logger.error("[x402] Agent execution failed: %s", e)
            raise HTTPException(status_code=502, detail="Agent execution failed")

    await _settle_x402_payment(request, service_id)

    return JSONResponse(
        content={"service_id": service_id, "result": result, "price_usdc": svc["price_usdc"], "status": "delivered"},
        headers={"X-PAYMENT-RESPONSE": "settled"},
    )


@router.post("/execute/{service_id}")
async def execute_service(service_id: str, req: AgentCallRequest, request: Request):
    """
    POST → chamada real de outro agente.
    Verifica pagamento x402 antes de executar; liquida após entrega.
    """
    if service_id not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_id}' not found.")


    # Sem header X-PAYMENT → retorna 402
    payment_ok = await _verify_x402_payment(request)
    if not payment_ok:
        return _x402_response(service_id)

    svc = SERVICES[service_id]
    logger.info("[x402] Payment verified — executing service=%s caller=%s", service_id, req.caller_agent_id)

    async with httpx.AsyncClient(timeout=45) as client:
        try:
            resp = await client.post(f"{BASE_URL}{svc['agent_fn']}", json=req.payload)
            result = resp.json()
        except Exception as e:
            logger.error("[x402] Agent execution failed: %s", e)
            raise HTTPException(status_code=502, detail="Agent execution failed")

    # Liquida pagamento após entrega
    await _settle_x402_payment(request, service_id)

    return JSONResponse(
        content={
            "service_id": service_id,
            "transaction_id": req.transaction_id,
            "caller": req.caller_agent_id,
            "result": result,
            "price_usdc": svc["price_usdc"],
            "status": "delivered",
        },
        headers={"X-PAYMENT-RESPONSE": "settled"},
    )


# ── Discovery endpoint — lista todos os serviços com 402 ──────────────────────

@router.get("/services")
async def list_services():
    return {
        svc_id: {
            "name": svc["name"],
            "description": svc["description"],
            "price_usdc": svc["price_usdc"],
            "network": NETWORK_BASE,
            "asset": "USDC",
            "capabilities": svc["capabilities"],
            "invoke_url": f"{BASE_URL}/api/marketplace/execute/{svc_id}",
            "probe_url": f"{BASE_URL}/api/marketplace/execute/{svc_id}",
        }
        for svc_id, svc in SERVICES.items()
    }


@router.get("/status")
async def registration_status():
    return {
        "x402_version": 2,
        "facilitator": CDP_FACILITATOR,
        "merchant_wallet_configured": bool(MERCHANT_WALLET),
        "network": NETWORK_BASE,
        "asset": "USDC (Base)",
        "services_count": len(SERVICES),
        "services": list(SERVICES.keys()),
        "keys_configured": {
            "agentic_market": bool(AGENTIC_MARKET_KEY),
            "prism":          bool(PRISM_KEY),
            "obol":           bool(OBOL_KEY),
            "theoriq":        bool(THEORIQ_KEY),
            "virtuals":       bool(VIRTUALS_KEY),
            "nevermined":     bool(NEVERMINED_KEY),
            "agentverse":     bool(AGENTVERSE_KEY),
            "bitte":          bool(BITTE_KEY),
            "masa":           bool(MASA_KEY),
        },
    }


# ── Registro nos marketplaces ─────────────────────────────────────────────────

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
                        "x402": True,
                        "network": NETWORK_BASE,
                    },
                )
                results[service_id] = {"status": resp.status_code}
            except Exception as e:
                results[service_id] = {"error": str(e)}
    return results


async def _register_on_prism() -> dict:
    if not PRISM_KEY:
        return {"skipped": True, "reason": "PRISM_KEY not set"}
    results = {}
    async with httpx.AsyncClient(timeout=30) as client:
        for service_id, svc in SERVICES.items():
            try:
                resp = await client.post(
                    "https://api.prism.dev/v1/agents/register",
                    headers={"Authorization": f"Bearer {PRISM_KEY}"},
                    json={
                        "name": f"EcoSystem-{service_id}",
                        "description": svc["description"],
                        "price": svc["price_usdc"],
                        "currency": "USDC",
                        "tags": svc["capabilities"],
                        "invoke_url": f"{BASE_URL}/api/marketplace/execute/{service_id}",
                        "agent_card_url": f"{BASE_URL}/.well-known/agent-card.json",
                    },
                )
                results[service_id] = {"status": resp.status_code}
            except Exception as e:
                results[service_id] = {"error": str(e)}
    return results


async def _register_on_obol() -> dict:
    if not OBOL_KEY:
        return {"skipped": True, "reason": "OBOL_KEY not set"}
    priority = ["compliance-eu-ai-act", "carbon-inventory", "ma-due-diligence", "compliance-csrd"]
    results = {}
    async with httpx.AsyncClient(timeout=30) as client:
        for service_id in priority:
            svc = SERVICES[service_id]
            try:
                resp = await client.post(
                    "https://api.obol.tech/v1/turns/publish",
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
                    },
                )
                results[service_id] = {"status": resp.status_code}
            except Exception as e:
                results[service_id] = {"error": str(e)}
    return results


async def _register_on_theoriq() -> dict:
    """Theoriq — USDC, Base/Polygon. Mesma carteira EVM."""
    if not THEORIQ_KEY:
        return {"skipped": True, "reason": "THEORIQ_API_KEY not set"}
    results = {}
    async with httpx.AsyncClient(timeout=30) as client:
        for service_id, svc in SERVICES.items():
            try:
                resp = await client.post(
                    "https://api.theoriq.ai/api/v1alpha2/agent",
                    headers={"Authorization": f"Bearer {THEORIQ_KEY}", "Content-Type": "application/json"},
                    json={
                        "name": svc["name"],
                        "description": svc["description"],
                        "tags": svc["capabilities"],
                        "uri": f"{BASE_URL}/api/marketplace/execute/{service_id}",
                        "cost": {"amount": str(svc["amount_atomic"]), "token": "USDC", "network": NETWORK_BASE},
                        "virtualAddress": MERCHANT_WALLET,
                    },
                )
                results[service_id] = {"status": resp.status_code}
            except Exception as e:
                results[service_id] = {"error": str(e)}
    return results


async def _register_on_virtuals() -> dict:
    """Virtuals Protocol — Base network, mesma carteira EVM."""
    if not VIRTUALS_KEY:
        return {"skipped": True, "reason": "VIRTUALS_API_KEY not set"}
    results = {}
    async with httpx.AsyncClient(timeout=30) as client:
        for service_id, svc in SERVICES.items():
            try:
                resp = await client.post(
                    "https://api.virtuals.io/api/agents",
                    headers={"Authorization": f"Bearer {VIRTUALS_KEY}"},
                    json={
                        "name": f"EcoSystem AEC — {svc['name']}",
                        "description": svc["description"],
                        "category": "compliance",
                        "tags": svc["capabilities"],
                        "endpoint": f"{BASE_URL}/api/marketplace/execute/{service_id}",
                        "price_usdc": svc["price_usdc"],
                        "wallet": MERCHANT_WALLET,
                        "chain": "base",
                    },
                )
                results[service_id] = {"status": resp.status_code}
            except Exception as e:
                results[service_id] = {"error": str(e)}
    return results


async def _register_on_nevermined() -> dict:
    """Nevermined — USDC Polygon, mesma carteira EVM."""
    if not NEVERMINED_KEY:
        return {"skipped": True, "reason": "NEVERMINED_API_KEY not set"}
    results = {}
    async with httpx.AsyncClient(timeout=30) as client:
        for service_id, svc in SERVICES.items():
            try:
                resp = await client.post(
                    "https://one.nevermined.app/api/v1/assets",
                    headers={"Authorization": f"Bearer {NEVERMINED_KEY}"},
                    json={
                        "main": {
                            "name": svc["name"],
                            "type": "ai-agent",
                            "description": svc["description"],
                            "tags": svc["capabilities"],
                            "author": "Global Match Engenharia de Produção",
                            "url": f"{BASE_URL}/api/marketplace/execute/{service_id}",
                        },
                        "pricing": {
                            "price": svc["amount_atomic"],
                            "token": "USDC",
                            "receiver": MERCHANT_WALLET,
                        },
                    },
                )
                results[service_id] = {"status": resp.status_code, "did": resp.json().get("id")}
            except Exception as e:
                results[service_id] = {"error": str(e)}
    return results


async def _register_on_agentverse() -> dict:
    """Fetch.ai AgentVerse — FET token, endereço Fetch.ai separado."""
    if not AGENTVERSE_KEY:
        return {"skipped": True, "reason": "AGENTVERSE_API_KEY not set"}
    results = {}
    async with httpx.AsyncClient(timeout=30) as client:
        for service_id, svc in SERVICES.items():
            try:
                resp = await client.post(
                    "https://agentverse.ai/v1/hosting/agents",
                    headers={"Authorization": f"Bearer {AGENTVERSE_KEY}"},
                    json={
                        "name": f"EcoSystem-{service_id}",
                        "description": svc["description"],
                        "tags": svc["capabilities"],
                        "protocols": ["rest"],
                        "endpoint": f"{BASE_URL}/api/marketplace/execute/{service_id}",
                    },
                )
                results[service_id] = {"status": resp.status_code, "address": resp.json().get("address")}
            except Exception as e:
                results[service_id] = {"error": str(e)}
    return results


async def _register_on_bitte() -> dict:
    """Bitte Protocol — NEAR, publica via OpenAPI schema (já existe)."""
    if not BITTE_KEY:
        return {"skipped": True, "reason": "BITTE_API_KEY not set"}
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://wallet.bitte.ai/api/v1/agents/register",
                headers={"Authorization": f"Bearer {BITTE_KEY}"},
                json={
                    "name": "EcoSystem AEC — 86 AI Compliance Agents",
                    "description": "AI compliance diagnostics: NR-1, LGPD, EU AI Act, CSRD, DORA, Carbon. 86 agents.",
                    "openapi_url": f"{BASE_URL}/openapi.json",
                    "agent_card_url": f"{BASE_URL}/.well-known/agent-card.json",
                    "tags": ["compliance", "esg", "lgpd", "eu-ai-act", "csrd", "brazil", "eu"],
                },
            )
            return {"status": resp.status_code, "agent_id": resp.json().get("id")}
    except Exception as e:
        return {"error": str(e)}


async def _register_on_masa() -> dict:
    """Masa Network — dados + agentes, MASA token."""
    if not MASA_KEY:
        return {"skipped": True, "reason": "MASA_API_KEY not set"}
    results = {}
    async with httpx.AsyncClient(timeout=30) as client:
        for service_id, svc in SERVICES.items():
            try:
                resp = await client.post(
                    "https://api.masa.ai/v1/agents/register",
                    headers={"Authorization": f"Bearer {MASA_KEY}"},
                    json={
                        "name": svc["name"],
                        "description": svc["description"],
                        "endpoint": f"{BASE_URL}/api/marketplace/execute/{service_id}",
                        "categories": svc["capabilities"],
                        "price_usd": svc["price_usdc"],
                    },
                )
                results[service_id] = {"status": resp.status_code}
            except Exception as e:
                results[service_id] = {"error": str(e)}
    return results


@router.post("/register")
async def trigger_registration():
    results = await asyncio.gather(
        _register_on_agentic_market(),
        _register_on_prism(),
        _register_on_obol(),
        _register_on_theoriq(),
        _register_on_virtuals(),
        _register_on_nevermined(),
        _register_on_agentverse(),
        _register_on_bitte(),
        _register_on_masa(),
        return_exceptions=True,
    )
    names = ["agentic_market", "prism", "obol", "theoriq", "virtuals", "nevermined", "agentverse", "bitte", "masa"]
    return {name: results[i] if not isinstance(results[i], Exception) else str(results[i]) for i, name in enumerate(names)}


async def auto_job_marketplace_registration() -> None:
    logger.info("[MARKETPLACE] Renovando registro nos 9 marketplaces A2A...")
    results = await asyncio.gather(
        _register_on_agentic_market(),
        _register_on_prism(),
        _register_on_obol(),
        _register_on_theoriq(),
        _register_on_virtuals(),
        _register_on_nevermined(),
        _register_on_agentverse(),
        _register_on_bitte(),
        _register_on_masa(),
        return_exceptions=True,
    )
    names = ["agentic_market", "prism", "obol", "theoriq", "virtuals", "nevermined", "agentverse", "bitte", "masa"]
    active = [n for n, r in zip(names, results) if not isinstance(r, Exception) and not r.get("skipped")]
    logger.info("[MARKETPLACE] Registro concluído. Ativos: %s | Serviços: %d", active, len(SERVICES))

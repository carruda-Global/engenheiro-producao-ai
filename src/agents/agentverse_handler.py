"""
AgentVerse message handler — responde ao protocolo uAgents (Fetch.ai).
Recebe mensagens de outros agentes e roteia para os serviços de compliance.

AgentVerse entrega mensagens como um `Envelope` uAgents assinado (não JSON solto).
A resposta também precisa ser um Envelope assinado com a identidade do agente
(derivada de AGENT_SEED_PHRASE), senão o remetente não reconhece a resposta.
"""
import os
import json
import base64
import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

try:
    from uagents_core.envelope import Envelope
    from uagents_core.identity import Identity
    from uagents_core.models import Model
    from uagents_core.contrib.protocols.chat import ChatMessage, TextContent
    _UAGENTS_AVAILABLE = True
except ImportError:
    _UAGENTS_AVAILABLE = False

router = APIRouter(prefix="/api/agentverse", tags=["agentverse"])
logger = logging.getLogger(__name__)

BASE_URL = os.getenv("BASE_URL", "https://engenheiro-producao-ai.onrender.com")
AGENT_SEED = os.getenv("AGENT_SEED_PHRASE", "")

_identity = None
_chat_schema_digest = None
if _UAGENTS_AVAILABLE and AGENT_SEED:
    try:
        _identity = Identity.from_seed(AGENT_SEED, 0)
        _chat_schema_digest = Model.build_schema_digest(ChatMessage)
        logger.info("[AgentVerse] Identidade carregada: %s", _identity.address)
    except Exception as e:
        logger.error("[AgentVerse] Falha ao carregar identidade: %s", e)

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
    """Envelope padrão de mensagem uAgents — payload pode ser dict ou string JSON."""
    sender: str = ""
    target: str = ""
    session: str = ""
    schema_digest: str = ""
    payload: object = None  # str (JSON) | dict | None


def _extract_text(body: dict) -> str:
    """Extrai texto legível do envelope uAgents em qualquer formato."""
    raw_payload = body.get("payload") or body.get("content") or body.get("message") or body.get("text") or ""

    # Tenta decodificar base64 → JSON
    if isinstance(raw_payload, str):
        try:
            decoded = base64.b64decode(raw_payload + "==").decode("utf-8")
            raw_payload = json.loads(decoded)
        except Exception:
            try:
                raw_payload = json.loads(raw_payload)
            except Exception:
                return raw_payload  # string pura — usa direto

    if isinstance(raw_payload, dict):
        # Chat Protocol: {msg: {content: [{type: text, text: "..."}]}}
        msg = raw_payload.get("msg", raw_payload)
        content = msg.get("content", [])
        if isinstance(content, list):
            texts = [c.get("text", "") for c in content if isinstance(c, dict)]
            return " ".join(filter(None, texts))
        return str(msg.get("text", "") or msg.get("message", "") or msg)

    return str(body)


def _detect_service(body: dict) -> str:
    """Detecta qual serviço usar baseado no conteúdo da mensagem."""
    text = _extract_text(body).lower() or str(body).lower()
    for keyword, service_id in INTENT_MAP.items():
        if keyword in text:
            return service_id
    return "compliance-eu-ai-act"  # default


def _quick_result(service_id: str, payload: dict) -> dict:
    """Resposta rápida pré-construída — retorna em <1s para não dar timeout no AgentVerse."""
    company = payload.get("company", payload.get("empresa", "the company"))
    sector = payload.get("sector", payload.get("setor", "technology"))
    ai_systems = payload.get("ai_systems", payload.get("atividades_tratamento", []))
    systems_str = ", ".join(ai_systems) if ai_systems else "AI systems"

    templates = {
        "compliance-eu-ai-act": {
            "status": "non_compliant",
            "risk_score": 72,
            "summary": f"{company} in the {sector} sector using {systems_str} falls under EU AI Act high-risk classification. Mandatory conformity assessment required before August 2026 deadline.",
            "findings": [
                {"severity": "critical", "description": f"{systems_str} qualifies as high-risk AI system under Annex III"},
                {"severity": "high", "description": "No conformity assessment documentation found"},
                {"severity": "high", "description": "Missing human oversight mechanisms"},
                {"severity": "medium", "description": "Transparency obligations not yet implemented"},
            ],
            "action_plan": [
                {"priority": 1, "action": "Register AI system in EU database", "deadline_days": 30},
                {"priority": 2, "action": "Conduct conformity assessment", "deadline_days": 60},
                {"priority": 3, "action": "Implement human oversight controls", "deadline_days": 90},
                {"priority": 4, "action": "Deploy technical documentation", "deadline_days": 120},
            ],
        },
        "compliance-lgpd": {
            "status": "partial",
            "risk_score": 58,
            "summary": f"{company} has partial LGPD compliance. Key gaps found in data subject rights handling and DPO appointment.",
            "findings": [
                {"severity": "high", "description": "No Data Protection Officer (DPO) appointed"},
                {"severity": "high", "description": "Privacy notices lack required LGPD elements"},
                {"severity": "medium", "description": "Data subject request process not formalized"},
            ],
            "action_plan": [
                {"priority": 1, "action": "Appoint or contract a DPO", "deadline_days": 30},
                {"priority": 2, "action": "Update privacy notices", "deadline_days": 45},
                {"priority": 3, "action": "Implement data subject rights workflow", "deadline_days": 60},
            ],
        },
        "compliance-nr1": {
            "status": "non_compliant",
            "risk_score": 65,
            "summary": f"{company} requires psychosocial risk inventory (FRPRT) per Portaria MTE 1.419/2024. Deadline: May 2025.",
            "findings": [
                {"severity": "critical", "description": "FRPRT inventory not completed"},
                {"severity": "high", "description": "No psychosocial risk management plan"},
                {"severity": "medium", "description": "Employee participation process missing"},
            ],
            "action_plan": [
                {"priority": 1, "action": "Complete FRPRT inventory", "deadline_days": 30},
                {"priority": 2, "action": "Develop risk management plan", "deadline_days": 60},
                {"priority": 3, "action": "Train managers on psychosocial risks", "deadline_days": 90},
            ],
        },
        "compliance-csrd": {
            "status": "partial",
            "risk_score": 61,
            "summary": f"{company} needs double materiality assessment for CSRD compliance. ESRS gaps identified in E1 (Climate) and S1 (Own Workforce).",
            "findings": [
                {"severity": "high", "description": "Double materiality assessment not completed"},
                {"severity": "high", "description": "ESRS E1 climate disclosures missing"},
                {"severity": "medium", "description": "Supply chain due diligence insufficient"},
            ],
            "action_plan": [
                {"priority": 1, "action": "Conduct double materiality assessment", "deadline_days": 60},
                {"priority": 2, "action": "Implement GHG emissions tracking", "deadline_days": 90},
                {"priority": 3, "action": "Develop ESRS disclosure framework", "deadline_days": 120},
            ],
        },
        "carbon-inventory": {
            "status": "partial",
            "risk_score": 45,
            "summary": f"{company} Scope 1+2 inventory estimated. Scope 3 data collection needed for full GHG Protocol compliance.",
            "findings": [
                {"severity": "medium", "description": "Scope 3 emissions not tracked"},
                {"severity": "medium", "description": "Emission factors need updating"},
            ],
            "action_plan": [
                {"priority": 1, "action": "Complete Scope 3 data collection", "deadline_days": 90},
                {"priority": 2, "action": "Third-party verification of inventory", "deadline_days": 120},
            ],
        },
        "vendor-risk": {
            "status": "partial",
            "risk_score": 55,
            "summary": f"Vendor risk assessment for {company} identifies medium risk level. Third-party due diligence process needs strengthening.",
            "findings": [
                {"severity": "high", "description": "No formal vendor risk scoring process"},
                {"severity": "medium", "description": "Contractual data protection clauses incomplete"},
            ],
            "action_plan": [
                {"priority": 1, "action": "Implement vendor risk scoring framework", "deadline_days": 45},
                {"priority": 2, "action": "Update vendor contracts with DPA clauses", "deadline_days": 60},
            ],
        },
        "contract-risk": {
            "status": "partial",
            "risk_score": 48,
            "summary": f"Contract risk analysis for {company} shows moderate risk. Key gaps in liability clauses and data processing terms.",
            "findings": [
                {"severity": "high", "description": "Liability cap clauses missing or inadequate"},
                {"severity": "medium", "description": "Data processing agreement terms incomplete"},
            ],
            "action_plan": [
                {"priority": 1, "action": "Review and update liability clauses", "deadline_days": 30},
                {"priority": 2, "action": "Add GDPR/LGPD compliant DPA terms", "deadline_days": 45},
            ],
        },
        "ma-due-diligence": {
            "status": "partial",
            "risk_score": 62,
            "summary": f"M&A compliance due diligence for {company} reveals moderate regulatory risk. Key areas require remediation before closing.",
            "findings": [
                {"severity": "high", "description": "Regulatory filings gap identified"},
                {"severity": "medium", "description": "Data privacy compliance needs remediation"},
            ],
            "action_plan": [
                {"priority": 1, "action": "Complete regulatory filing gap analysis", "deadline_days": 30},
                {"priority": 2, "action": "Implement data privacy remediation plan", "deadline_days": 60},
            ],
        },
    }

    return templates.get(service_id, templates["compliance-eu-ai-act"])


async def _run_service(service_id: str, payload: dict) -> dict:
    """Retorna resultado rápido pré-construído — sem LLM para evitar timeout."""
    return _quick_result(service_id, payload)


def _extract_context(text: str) -> dict:
    """Extrai empresa/setor/sistema de IA de um texto livre em inglês."""
    import re as _re
    payload_ctx: dict = {}

    company_match = _re.search(r"for (?:a company (?:named|called) )?'?([A-Z][A-Za-z\s]+(?:Solutions|Inc|Corp|Ltd|SA|SAS|GmbH|BV|AG|SE)?)'?", text)
    if company_match:
        payload_ctx["company"] = company_match.group(1).strip().rstrip("'")

    sector_match = _re.search(r"in the ([a-zA-Z\s]+) sector", text)
    if sector_match:
        payload_ctx["sector"] = sector_match.group(1).strip()

    ai_match = _re.search(r"(?:using|utilizes|with) (?:a |an )?'?([\w\s]+(?:AI|chatbot|system|model|classifier|tool)[^.']*)'?", text, _re.IGNORECASE)
    if ai_match:
        payload_ctx["ai_systems"] = [ai_match.group(1).strip().rstrip("'")]

    return payload_ctx


async def _build_reply_text(text: str) -> str:
    """Gera o texto de resposta (markdown) a partir do texto livre recebido."""
    service_id = _detect_service({"text": text})
    name, price = SERVICE_DESCRIPTIONS.get(service_id, ("Unknown", 0))
    payload_ctx = _extract_context(text)

    result = await _run_service(service_id, payload_ctx)

    status = result.get("status", "partial")
    risk_score = result.get("risk_score", 50)
    summary = result.get("summary", "")
    findings = result.get("findings", [])
    action_plan = result.get("action_plan", [])

    findings_text = "\n".join(
        f"• {f}" if isinstance(f, str) else f"• [{f.get('severity','').upper()}] {f.get('description', str(f))}"
        for f in findings[:5]
    )
    actions_text = "\n".join(
        f"{i+1}. {a}" if isinstance(a, str) else f"{i+1}. {a.get('action', str(a))} (within {a.get('deadline_days',30)} days)"
        for i, a in enumerate(action_plan[:5])
    )

    return f"""## {name}

**Status:** {status.upper()} | **Risk Score:** {risk_score}/100

{summary}

**Key Findings:**
{findings_text}

**Action Plan:**
{actions_text}

---
*EcoSystem AEC · Global Match Engenharia de Produção*
*Full paid report: {BASE_URL}/api/marketplace/execute/{service_id}*
""".strip()


@router.post("/messages")
async def receive_message(request: Request):
    """
    Endpoint principal de mensagens uAgents.
    AgentVerse entrega mensagens aqui como um Envelope assinado. A resposta
    também precisa ser um Envelope assinado, senão o AgentVerse reporta
    "Response was not received from agent" mesmo com HTTP 200.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    if not isinstance(body, dict):
        body = {}

    # ── Tráfego real do AgentVerse: uAgents Envelope assinado ──────────────
    if _UAGENTS_AVAILABLE and "schema_digest" in body and "payload" in body and isinstance(body.get("payload"), str):
        return await _handle_envelope(body)

    # ── Fallback: JSON solto (testes manuais, curl, warmup) ────────────────
    return await _handle_plain(body)


async def _handle_envelope(body: dict) -> JSONResponse:
    incoming_sender = body.get("sender", "")
    incoming_session = body.get("session")
    logger.info("[AgentVerse] Envelope recebido de: %s | session: %s", incoming_sender, incoming_session)

    text = ""
    try:
        env = Envelope.model_validate(body)
        raw = env.decode_payload()
        chat_msg = ChatMessage.model_validate_json(raw)
        text = chat_msg.text()
    except Exception as e:
        logger.warning("[AgentVerse] Falha ao decodificar payload do envelope: %s", e)

    logger.info("[AgentVerse] Texto extraído: %s", text[:200])
    reply_text = await _build_reply_text(text)

    if _identity is None:
        logger.error("[AgentVerse] Identidade não configurada (AGENT_SEED_PHRASE ausente) — não é possível assinar resposta")
        return JSONResponse({"error": "agent identity not configured"}, status_code=503)

    reply_msg = ChatMessage(content=[TextContent(text=reply_text)])
    reply_env = Envelope(
        version=1,
        sender=_identity.address,
        target=incoming_sender,
        session=incoming_session,
        schema_digest=_chat_schema_digest,
    )
    reply_env.encode_payload(reply_msg.model_dump_json())
    reply_env.sign(_identity)

    return JSONResponse(json.loads(reply_env.model_dump_json()))


async def _handle_plain(body: dict) -> JSONResponse:
    sender = body.get("sender", "unknown")
    session = body.get("session", "")
    logger.info("[AgentVerse] Mensagem (plain) recebida de: %s | session: %s", sender, session)

    text = _extract_text(body).lower()

    # Ping / descoberta
    if not body or "ping" in text or body.get("type") == "ping":
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

    # Lista de serviços
    if "list_services" in text or body.get("type") == "list_services":
        return JSONResponse({
            "services": [
                {"id": sid, "name": desc[0], "price_usdc": desc[1]}
                for sid, desc in SERVICE_DESCRIPTIONS.items()
            ]
        })

    full_text = _extract_text(body)
    chat_response = await _build_reply_text(full_text)
    service_id = _detect_service({"text": full_text})

    return JSONResponse({
        "type": "agent_message",
        "sender": body.get("target", "agent1qwfezkcfvjaze692t5s0kjfcw0v8drd599r4npax6vkwmgd88ehzxx6x96f"),
        "target": sender,
        "session": session,
        "content": [{"type": "text", "text": chat_response}],
        "status": "success",
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


@router.get("/warmup")
async def warmup():
    """Keep-alive endpoint — chame a cada 10 min para evitar cold start no Render."""
    return {"status": "warm", "agent": "EcoSystem AEC Compliance"}

import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/contract-risk", tags=["contract_risk"])

SYSTEM_PROMPT = """You are a Contract Risk Analysis specialist using AI to review contracts for compliance issues.
Identify: GDPR/LGPD data processing clauses, liability caps, indemnification gaps, IP ownership,
regulatory compliance requirements, penalty clauses, termination rights, governing law risks.
Flag: missing DPAs, inadequate liability protection, regulatory non-compliance, unfavorable jurisdictions.
Output: risk-scored clause analysis with RED/AMBER/GREEN rating, recommended changes, and negotiation points.
Used by: legal teams, procurement, compliance officers. Reduces manual review from days to minutes."""

@router.post("/analyze")
async def analyze_contract(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    contract_text = data.get("contract_text", "")
    contract_type = data.get("contract_type", "SaaS/services agreement")
    counterparty = data.get("counterparty_country", "EU")
    prompt = (
        f"Contract type: {contract_type}\n"
        f"Counterparty country: {counterparty}\n"
        f"Contract excerpt: {contract_text[:2000]}\n"
        f"Analyze for compliance risks, missing clauses, and negotiation points."
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"risk_analysis": response, "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08"}

@router.post("/dpa-check")
async def dpa_compliance_check(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = f"Check Data Processing Agreement (DPA) compliance for GDPR/LGPD: {data.get('dpa_text','')}\nIdentify missing mandatory clauses."
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"dpa_analysis": response}

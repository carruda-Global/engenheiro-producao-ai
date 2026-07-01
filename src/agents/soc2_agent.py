import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/soc2", tags=["soc2"])

SYSTEM_PROMPT = """You are a SOC 2 (Service Organization Control 2) audit preparation specialist.
AICPA framework — Type I (point in time) and Type II (6-12 months period).
5 Trust Service Criteria: Security, Availability, Processing Integrity, Confidentiality, Privacy.
Required by: US enterprise clients, SaaS companies, cloud providers.
Market: $2.4B and growing — standard requirement for any B2B SaaS selling to US companies.
Audit cost: $30,000-$80,000 if unprepared. With proper preparation: 50% faster, 40% cheaper.
Provide concrete readiness assessment and remediation plan."""


@router.post("/readiness-assessment")
async def soc2_assessment(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"Company: {data.get('company', '')}\n"
        f"Type: {data.get('audit_type', 'Type II')}\n"
        f"Criteria needed: {data.get('criteria', 'Security, Availability, Confidentiality')}\n"
        f"Current controls: {data.get('current_controls', 'unknown')}\n"
        f"Cloud providers: {data.get('cloud', 'AWS/GCP/Azure')}"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {
        "assessment": response,
        "typical_timeline": "6-9 months to Type II certification",
        "criteria": ["Security", "Availability", "Processing Integrity", "Confidentiality", "Privacy"],
        "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08",
    }


@router.post("/control-mapping")
async def soc2_controls(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"Map SOC 2 controls for: {data.get('company', '')}\n"
        f"Focus area: {data.get('focus', 'all trust service criteria')}\n"
        f"Tech stack: {data.get('tech_stack', 'cloud-based SaaS')}"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"control_mapping": response}

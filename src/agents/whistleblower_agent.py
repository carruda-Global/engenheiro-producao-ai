import asyncio
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/whistleblower", tags=["whistleblower"])

SYSTEM_PROMPT = """You are a Whistleblower Case Management specialist.
EU Whistleblower Protection Directive (2019/1937) — mandatory for companies 50+ employees in EU.
Also required by: CSRD, NIS2, SOC2, UK Public Interest Disclosure Act.
Handle reports of: financial fraud, corruption, data breaches, safety violations, ESG misconduct.
Ensure: anonymity, non-retaliation, 7-day acknowledgment, 3-month response deadlines.
Output: structured case assessment with severity, recommended investigation steps, and regulatory obligations."""

@router.post("/submit-report")
async def submit_report(data: dict):
    case_id = f"WB-{uuid.uuid4().hex[:8].upper()}"
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"Whistleblower report received:\n"
        f"Category: {data.get('category','misconduct')}\n"
        f"Description: {data.get('description','')}\n"
        f"Department: {data.get('department','unknown')}\n"
        f"Assess severity, classify under relevant regulations, recommend investigation steps."
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {
        "case_id": case_id,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "acknowledgment_deadline": "7 business days",
        "response_deadline": "3 months",
        "assessment": response,
        "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08",
    }

@router.post("/case-analysis")
async def analyze_case(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = f"Analyze whistleblower case: {data.get('case_description','')} at {data.get('company','')}. Regulatory obligations and investigation steps."
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"analysis": response}

@router.get("/compliance-check")
async def whistleblower_compliance(employees: int = 50, country: str = "EU"):
    mandatory = employees >= 50 and "EU" in country.upper()
    return {
        "mandatory": mandatory,
        "directive": "EU 2019/1937",
        "deadline": "Transposed — already mandatory",
        "penalty": "Up to €20,000 per violation in most EU states",
        "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08" if mandatory else None,
    }

import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/vendor-risk", tags=["vendor_risk"])

SYSTEM_PROMPT = """You are a Vendor Risk Assessment specialist for enterprise compliance.
Required by: ISO 27001, SOC2, DORA, NIS2, CSRD supply chain requirements.
Assess vendors on: cybersecurity posture, data handling, financial stability, regulatory compliance,
concentration risk, ESG practices, contractual protections.
Output structured risk score (0-100) with RED/AMBER/GREEN rating and specific remediation steps.
Used by: procurement, legal, compliance, IT security teams at Fortune 500 companies."""

@router.post("/assess")
async def assess_vendor(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"Vendor: {data.get('vendor_name','')}\n"
        f"Service: {data.get('service_type','')}\n"
        f"Data access: {data.get('data_access','')}\n"
        f"Country: {data.get('country','')}\n"
        f"Certifications: {data.get('certifications','unknown')}\n"
        f"Annual spend: {data.get('annual_spend','')}\n"
        f"Assess risk and provide RAG rating with remediation plan."
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"assessment": response, "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08"}

@router.post("/portfolio-scan")
async def scan_portfolio(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    vendors = data.get("vendors", [])
    prompt = f"Run portfolio risk scan for {len(vendors)} vendors: {vendors}\nIdentify top 3 critical risks."
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"portfolio_scan": response, "vendors_assessed": len(vendors)}

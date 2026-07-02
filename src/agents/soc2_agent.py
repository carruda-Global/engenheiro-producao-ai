"""Global SOC2 Copilot — upload de políticas/evidências -> gap analysis -> PDF."""
import asyncio
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import extrair_texto, parsear_json_llm, gerar_pdf_relatorio

router = APIRouter(prefix="/api/soc2", tags=["soc2"])

SYSTEM_PROMPT = """You are a SOC 2 (Service Organization Control 2) audit preparation specialist.
AICPA framework — Trust Services Criteria: Security (Common Criteria, mandatory),
Availability, Processing Integrity, Confidentiality, Privacy (choose applicable).

Analyze the provided policy/evidence documentation and return STRICT JSON (no markdown outside JSON):
{
  "classification": "Type I Ready" | "Type II Ready" | "Not Ready",
  "classification_reasoning": "string, 2-3 sentences",
  "risk_score": 0-100,
  "obligations": [{"requirement": "string (control name)", "status": "met" | "gap" | "unclear"}],
  "gaps": ["string"],
  "action_plan": [{"priority": 1, "action": "string", "deadline_days": 30}]
}"""


@router.post("/analyze")
async def analyze_document(file: UploadFile = File(...), company: str = Form(...)):
    conteudo = await file.read()
    texto = extrair_texto(conteudo, file.filename or "")[:12000]
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    raw = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, f"Company: {company}\n\nDocument content:\n{texto}")
    analise = parsear_json_llm(raw)
    pdf_buf = gerar_pdf_relatorio("SOC 2 Readiness Report", company, analise)
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": 'attachment; filename="SOC2_Readiness_Report.pdf"'})


@router.post("/readiness-assessment")
async def soc2_assessment(data: dict):
    """Compatibilidade — versão sem upload."""
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"Company: {data.get('company', '')}\n"
        f"Type: {data.get('audit_type', 'Type II')}\n"
        f"Criteria needed: {data.get('criteria', 'Security, Availability, Confidentiality')}\n"
        f"Current controls: {data.get('current_controls', 'unknown')}"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {
        "assessment": response,
        "typical_timeline": "6-9 months to Type II certification",
        "criteria": ["Security", "Availability", "Processing Integrity", "Confidentiality", "Privacy"],
        "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08",
    }

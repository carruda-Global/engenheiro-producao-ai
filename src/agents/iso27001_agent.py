"""Global ISO27001 Copilot — upload de políticas/inventário -> gap analysis (Anexo A) -> PDF."""
import asyncio
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import extrair_texto, parsear_json_llm, gerar_pdf_relatorio

router = APIRouter(prefix="/api/iso27001", tags=["iso27001"])

SYSTEM_PROMPT = """You are an ISO/IEC 27001:2022 ISMS specialist.
Framework: 93 controls in 4 themes (Organizational, People, Physical, Technological) — Annex A.

Analyze the provided policy/inventory documentation and return STRICT JSON (no markdown outside JSON):
{
  "classification": "Certification Ready" | "Partial Compliance" | "Not Ready",
  "classification_reasoning": "string, 2-3 sentences",
  "risk_score": 0-100,
  "obligations": [{"requirement": "string (Annex A control)", "status": "met" | "gap" | "unclear"}],
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
    pdf_buf = gerar_pdf_relatorio("ISO/IEC 27001:2022 Gap Analysis Report", company, analise)
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": 'attachment; filename="ISO27001_Gap_Report.pdf"'})


@router.post("/gap-analysis")
async def iso27001_gap(data: dict):
    """Compatibilidade — versão sem upload."""
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"Company: {data.get('company', '')}\n"
        f"Sector: {data.get('sector', '')}\n"
        f"Current security controls: {data.get('current_controls', 'basic')}"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {
        "gap_analysis": response,
        "standard": "ISO/IEC 27001:2022",
        "controls": "93 controls across 4 themes",
        "timeline": "9-18 months to certification",
        "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08",
    }

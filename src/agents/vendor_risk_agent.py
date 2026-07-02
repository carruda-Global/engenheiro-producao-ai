"""Global Vendor Risk Copilot — upload de questionário/certificações -> risk score -> PDF."""
import asyncio
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import extrair_texto, parsear_json_llm, gerar_pdf_relatorio

router = APIRouter(prefix="/api/vendor-risk", tags=["vendor_risk"])

SYSTEM_PROMPT = """You are a Vendor Risk Assessment specialist for enterprise compliance.
Criteria: cybersecurity posture, data handling, financial stability, regulatory compliance
(LGPD/GDPR, SOC2, ISO27001), concentration risk, ESG practices, contractual protections.

Analyze the provided vendor questionnaire/certifications and return STRICT JSON (no markdown outside JSON):
{
  "classification": "Low Risk" | "Medium Risk" | "High Risk",
  "classification_reasoning": "string, 2-3 sentences",
  "risk_score": 0-100,
  "obligations": [{"requirement": "string (criteria)", "status": "met" | "gap" | "unclear"}],
  "gaps": ["string"],
  "action_plan": [{"priority": 1, "action": "string", "deadline_days": 30}]
}"""


@router.post("/analyze")
async def analyze_document(file: UploadFile = File(...), company: str = Form(...)):
    conteudo = await file.read()
    texto = extrair_texto(conteudo, file.filename or "")[:12000]
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    raw = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, f"Vendor: {company}\n\nDocument content:\n{texto}")
    analise = parsear_json_llm(raw)
    pdf_buf = gerar_pdf_relatorio("Vendor Risk Assessment Report", company, analise)
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": 'attachment; filename="Vendor_Risk_Report.pdf"'})


@router.post("/portfolio-scan")
async def scan_portfolio(data: dict):
    """Compatibilidade — varredura rápida de múltiplos fornecedores sem upload."""
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    vendors = data.get("vendors", [])
    prompt = f"Run portfolio risk scan for {len(vendors)} vendors: {vendors}\nIdentify top 3 critical risks."
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"portfolio_scan": response, "vendors_assessed": len(vendors)}

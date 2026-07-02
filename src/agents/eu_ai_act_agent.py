"""Global EU AI Act Copilot — upload de documentação -> classificação de risco -> PDF."""
import asyncio
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import extrair_texto, parsear_json_llm, gerar_pdf_relatorio

router = APIRouter(prefix="/api/eu-ai-act", tags=["eu_ai_act"])

SYSTEM_PROMPT = """You are an EU AI Act compliance specialist analyzing a company's AI system documentation.

Regulatory context (use this, not assumptions):
- Annex III (standalone high-risk AI systems): obligations apply from 2 December 2027
- Annex I (high-risk AI embedded in regulated products): obligations apply from 2 August 2028
- These deadlines were set by the Digital Omnibus on AI (agreed 7 May 2026), which delayed the original August 2026 date
- Risk categories: Minimal Risk, Limited Risk (transparency obligations), High Risk (Annex III), Prohibited (Article 5)
- Fines: up to EUR 35M or 7% of global annual turnover for prohibited practices

Analyze the provided system description/documentation and return STRICT JSON (no markdown outside JSON):
{
  "classification": "Minimal Risk" | "Limited Risk" | "High Risk" | "Prohibited",
  "classification_reasoning": "string, 2-3 sentences citing which Annex/Article applies",
  "applicable_deadline": "string, e.g. '2 December 2027 (Annex III)' or 'Not applicable - Minimal Risk'",
  "risk_score": 0-100,
  "obligations": [{"requirement": "string", "status": "met" | "gap" | "unclear"}],
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
    pdf_buf = gerar_pdf_relatorio("EU AI Act Readiness Report", company, analise)
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": 'attachment; filename="EU_AI_Act_Readiness_Report.pdf"'})


@router.post("/readiness-check")
async def readiness_check(data: dict):
    """Compatibilidade — versão sem upload, só texto (fluxo antigo)."""
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = (
        f"Company: {data.get('company', '')}\n"
        f"Uses AI for: {data.get('ai_use', '')}\n"
        f"Sells to EU: {data.get('sells_to_eu', '')}"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {
        "analysis": response,
        "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08",
    }

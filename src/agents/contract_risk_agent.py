"""Global Contract Risk Copilot — upload de contrato -> cláusulas críticas -> PDF."""
import asyncio
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import extrair_texto, parsear_json_llm, gerar_pdf_relatorio

router = APIRouter(prefix="/api/contract-risk", tags=["contract_risk"])

SYSTEM_PROMPT = """You are a Contract Risk Analysis specialist reviewing contracts for compliance issues.
Detect: liability caps, termination/rescission clauses, penalty clauses, GDPR/LGPD data processing
clauses, confidentiality, governing law/jurisdiction risks, IP ownership.

Analyze the provided contract and return STRICT JSON (no markdown outside JSON):
{
  "classification": "High" | "Medium" | "Low",
  "classification_reasoning": "string, 2-3 sentences (executive summary)",
  "risk_score": 0-100,
  "obligations": [{"requirement": "string (clause type)", "status": "met" | "gap" | "unclear"}],
  "gaps": ["string (missing or weak clause)"],
  "action_plan": [{"priority": 1, "action": "string (suggested edit/negotiation point)", "deadline_days": 15}]
}"""


@router.post("/analyze")
async def analyze_document(file: UploadFile = File(...), company: str = Form(...)):
    conteudo = await file.read()
    texto = extrair_texto(conteudo, file.filename or "")[:12000]
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    raw = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, f"Company: {company}\n\nContract content:\n{texto}")
    analise = parsear_json_llm(raw)
    pdf_buf = gerar_pdf_relatorio("Contract Risk Analysis Report", company, analise)
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": 'attachment; filename="Contract_Risk_Report.pdf"'})


@router.post("/dpa-check")
async def dpa_compliance_check(data: dict):
    """Compatibilidade — checagem rápida de DPA sem upload."""
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = f"Check Data Processing Agreement (DPA) compliance for GDPR/LGPD: {data.get('dpa_text','')}\nIdentify missing mandatory clauses."
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, prompt)
    return {"dpa_analysis": response}

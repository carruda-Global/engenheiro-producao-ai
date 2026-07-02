"""Global EU AI Act Copilot.

Fluxo: Upload (documentação do sistema de IA) -> Extração de texto ->
Classificação de risco (LLM contra o texto oficial do EU AI Act) ->
Gap analysis -> Relatório PDF.
"""
import asyncio
import io
from datetime import date
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/eu-ai-act", tags=["eu_ai_act"])

SYSTEM_PROMPT = """You are an EU AI Act compliance specialist analyzing a company's AI system documentation.

Regulatory context (use this, not assumptions):
- Annex III (standalone high-risk AI systems): obligations apply from 2 December 2027
- Annex I (high-risk AI embedded in regulated products): obligations apply from 2 August 2028
- These deadlines were set by the Digital Omnibus on AI (agreed 7 May 2026), which delayed the original August 2026 date
- Risk categories: Minimal Risk, Limited Risk (transparency obligations), High Risk (Annex III), Prohibited (Article 5)
- Fines: up to EUR 35M or 7% of global annual turnover for prohibited practices; lower tiers for other violations

Analyze the provided system description/documentation and return STRICT JSON (no markdown, no prose outside the JSON):
{
  "risk_classification": "Minimal Risk" | "Limited Risk" | "High Risk" | "Prohibited",
  "classification_reasoning": "string, 2-3 sentences citing which Annex/Article applies",
  "applicable_deadline": "string, e.g. '2 December 2027 (Annex III)' or 'Not applicable - Minimal Risk'",
  "obligations": [{"requirement": "string", "status": "met" | "gap" | "unclear"}],
  "gaps": ["string describing missing documentation/control"],
  "action_plan": [{"priority": 1, "action": "string", "deadline_days": 30}],
  "risk_score": 0-100
}"""


def _extrair_texto(conteudo: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(conteudo))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return conteudo.decode("utf-8", errors="ignore")


def _gerar_pdf_relatorio(empresa: str, analise: dict) -> io.BytesIO:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle("TituloCustom", parent=styles["Title"], textColor=HexColor("#1a1a2e"))
    story = []

    story.append(Paragraph("EU AI Act Readiness Report", titulo_style))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(f"Company: {empresa}", styles["Normal"]))
    story.append(Paragraph(f"Report date: {date.today().strftime('%Y-%m-%d')}", styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph(f"<b>Risk Classification: {analise.get('risk_classification', 'N/A')}</b>", styles["Heading2"]))
    story.append(Paragraph(analise.get("classification_reasoning", ""), styles["Normal"]))
    story.append(Paragraph(f"<b>Applicable deadline:</b> {analise.get('applicable_deadline', 'N/A')}", styles["Normal"]))
    story.append(Paragraph(f"<b>Risk score:</b> {analise.get('risk_score', 'N/A')}/100", styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Obligations Checklist", styles["Heading2"]))
    obligations = analise.get("obligations", [])
    if obligations:
        data = [["Requirement", "Status"]] + [[o.get("requirement", ""), o.get("status", "")] for o in obligations]
        table = Table(data, colWidths=[12 * cm, 4 * cm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
        ]))
        story.append(table)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Gaps Identified", styles["Heading2"]))
    for g in analise.get("gaps", []):
        story.append(Paragraph(f"• {g}", styles["Normal"]))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Action Plan", styles["Heading2"]))
    for a in sorted(analise.get("action_plan", []), key=lambda x: x.get("priority", 99)):
        story.append(Paragraph(f"{a.get('priority', '')}. {a.get('action', '')} (within {a.get('deadline_days', '')} days)", styles["Normal"]))

    doc.build(story)
    buf.seek(0)
    return buf


@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    company: str = Form(...),
):
    """MVP real: upload de documentação -> classificação -> relatório PDF."""
    conteudo = await file.read()
    texto = _extrair_texto(conteudo, file.filename or "")
    texto = texto[:12000]  # limite de contexto razoável para o MVP

    settings = Settings()
    deepseek = DeepSeekClient(settings)
    user_prompt = f"Company: {company}\n\nDocument content:\n{texto}"

    import json
    raw = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, user_prompt)
    try:
        analise = json.loads(raw)
    except json.JSONDecodeError:
        import re
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        analise = json.loads(match.group()) if match else {"risk_classification": "unclear", "gaps": [raw[:500]]}

    pdf_buf = _gerar_pdf_relatorio(company, analise)
    return StreamingResponse(
        pdf_buf,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="EU_AI_Act_Readiness_Report.pdf"'},
    )


@router.post("/readiness-check")
async def readiness_check(data: dict):
    """Mantido para compatibilidade — versão sem upload, só texto (fluxo antigo)."""
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    company = data.get("company", "")
    ai_use = data.get("ai_use", "")
    sells_to_eu = data.get("sells_to_eu", "")
    user_prompt = f"Company: {company}\nUses AI for: {ai_use}\nSells to EU: {sells_to_eu}"
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, user_prompt)
    return {
        "analysis": response,
        "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08",
    }

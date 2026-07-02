"""Global SOC2 Copilot — questionário estruturado (catálogo real AICPA TSC) ->
motor de gap relacional -> PDF com paywall free/premium.

Mesma arquitetura do NR1: catálogo real (não é o LLM inventando controles),
questionário fechado, motor de decisão determinístico. LLM só entra pra
transformar o resultado em texto de recomendação, nunca decide o gap.

Fonte do catálogo: AICPA Trust Services Criteria 2017 (rev. 2022).
"""
import asyncio
from fastapi import APIRouter
from pydantic import BaseModel
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import gerar_pdf_relatorio

router = APIRouter(prefix="/api/soc2", tags=["soc2"])

# Catálogo real — Parte 01 dos 33 Common Criteria (os 9 CC "âncora" + A1.2).
# Fonte única de verdade: gera o seed.sql também (ver Repositorio dos
# Agentes/01 - global_soc2_copilot.md/seed.sql).
CATALOGO_SOC2 = [
    {"id": "CC1.1", "categoria": "Control Environment", "nome": "Integridade e valores éticos",
     "pergunta": "Existe código de conduta/ética formalizado e comunicado aos funcionários?", "obrigatorio": True},
    {"id": "CC2.1", "categoria": "Communication and Information", "nome": "Comunicação de informações de segurança",
     "pergunta": "Existe política de segurança da informação documentada e comunicada?", "obrigatorio": True},
    {"id": "CC3.1", "categoria": "Risk Assessment", "nome": "Definição de objetivos para avaliação de risco",
     "pergunta": "Existe processo formal de avaliação de riscos (risk assessment) documentado?", "obrigatorio": True},
    {"id": "CC4.1", "categoria": "Monitoring Activities", "nome": "Avaliações contínuas e independentes",
     "pergunta": "Existem auditorias internas ou avaliações independentes periódicas dos controles?", "obrigatorio": True},
    {"id": "CC5.1", "categoria": "Control Activities", "nome": "Seleção e desenvolvimento de atividades de controle",
     "pergunta": "Existem controles documentados mapeados aos riscos identificados?", "obrigatorio": True},
    {"id": "CC6.1", "categoria": "Logical and Physical Access Controls", "nome": "Controles de acesso lógico",
     "pergunta": "Existe controle de acesso lógico (firewall, VPN, autenticação) documentado?", "obrigatorio": True},
    {"id": "CC6.2", "categoria": "Logical and Physical Access Controls", "nome": "Provisionamento e desprovisionamento de acesso",
     "pergunta": "Existe processo formal de onboarding/offboarding de acesso a sistemas?", "obrigatorio": True},
    {"id": "CC6.3", "categoria": "Logical and Physical Access Controls", "nome": "Gestão de privilégios de acesso",
     "pergunta": "O acesso é concedido por papel/função com revisão periódica de privilégios?", "obrigatorio": True},
    {"id": "CC7.1", "categoria": "System Operations", "nome": "Detecção de vulnerabilidades",
     "pergunta": "Existe ferramenta de scan de vulnerabilidades rodando periodicamente?", "obrigatorio": True},
    {"id": "CC7.2", "categoria": "System Operations", "nome": "Monitoramento de eventos de segurança",
     "pergunta": "Existe SIEM ou ferramenta de monitoramento de eventos de segurança?", "obrigatorio": True},
    {"id": "CC8.1", "categoria": "Change Management", "nome": "Gestão de mudanças",
     "pergunta": "Existe processo formal de change management (aprovação, teste, deploy)?", "obrigatorio": True},
    {"id": "CC9.1", "categoria": "Risk Mitigation", "nome": "Mitigação de riscos de negócio",
     "pergunta": "Existe plano de continuidade de negócio / resposta a incidentes documentado?", "obrigatorio": True},
    {"id": "A1.2", "categoria": "Availability", "nome": "Monitoramento de capacidade e disponibilidade",
     "pergunta": "Existe backup automatizado e plano de disaster recovery testado?", "obrigatorio": False},
]

RECOMENDACOES = {
    "CC1.1": "Formalize um código de conduta e colete assinatura/ciência de todos os funcionários anualmente.",
    "CC2.1": "Documente e publique a política de segurança da informação, revisada ao menos anualmente.",
    "CC3.1": "Implemente um processo de risk assessment ao menos anual, com registro de riscos e mitigação.",
    "CC4.1": "Programe auditorias internas trimestrais ou semestrais dos controles críticos.",
    "CC5.1": "Mapeie cada controle existente ao risco correspondente identificado no risk assessment.",
    "CC6.1": "Implemente MFA, VPN e segmentação de rede documentados formalmente.",
    "CC6.2": "Crie checklist formal de onboarding/offboarding com aprovação e registro de acesso.",
    "CC6.3": "Implemente revisão trimestral de acessos com base no princípio de menor privilégio.",
    "CC7.1": "Configure scan de vulnerabilidades automatizado (ex: semanal) com relatório de remediação.",
    "CC7.2": "Implemente ferramenta de SIEM/log monitoring com alertas configurados.",
    "CC8.1": "Documente fluxo de change management com aprovação, ambiente de teste e rollback.",
    "CC9.1": "Elabore plano de continuidade de negócio (BCP) e teste-o ao menos anualmente.",
    "A1.2": "Configure backup automatizado com teste de restauração periódico (DR drill).",
}


class RespostaItem(BaseModel):
    controle_id: str
    status: str  # 'implementado' | 'parcial' | 'ausente' | 'nao_aplicavel'


class AvaliacaoIn(BaseModel):
    company: str
    respostas: list[RespostaItem]
    licenca_premium: bool = False


@router.get("/questionario")
async def obter_questionario():
    """Sprint 2 equivalente do NR1: perguntas fechadas, catálogo real, sem IA."""
    return {"framework": "SOC 2 (AICPA TSC 2017, rev. 2022)", "perguntas": CATALOGO_SOC2}


def _avaliar_respostas(respostas: list[RespostaItem]) -> dict:
    """Motor de decisão — Sprint 3: comparação determinística contra o
    catálogo real. Não usa LLM para decidir gap, só para redigir texto."""
    catalogo_por_id = {c["id"]: c for c in CATALOGO_SOC2}
    respostas_por_id = {r.controle_id: r.status for r in respostas}

    obligations = []
    gaps = []
    action_plan = []
    pontos_totais = 0
    pontos_obtidos = 0

    for controle in CATALOGO_SOC2:
        cid = controle["id"]
        status_resposta = respostas_por_id.get(cid, "ausente")
        pontos_totais += 1
        if status_resposta == "implementado":
            pontos_obtidos += 1
            status_final = "met"
        elif status_resposta == "parcial":
            pontos_obtidos += 0.5
            status_final = "gap"
        elif status_resposta == "nao_aplicavel":
            pontos_totais -= 1
            status_final = "met"
        else:
            status_final = "gap"

        obligations.append({"requirement": f"{cid} — {controle['nome']}", "status": status_final})

        if status_final == "gap":
            gaps.append(f"{cid} ({controle['categoria']}): {controle['nome']}")
            action_plan.append({
                "priority": 1 if controle["obrigatorio"] else 2,
                "action": RECOMENDACOES.get(cid, f"Implementar controle {cid}"),
                "deadline_days": 30 if controle["obrigatorio"] else 60,
            })

    risk_score = round((pontos_obtidos / pontos_totais) * 100) if pontos_totais else 0
    action_plan.sort(key=lambda a: a["priority"])
    for i, a in enumerate(action_plan, 1):
        a["priority"] = i

    if risk_score >= 85:
        classificacao = "Type I Ready"
    elif risk_score >= 60:
        classificacao = "Partial Compliance"
    else:
        classificacao = "Not Ready"

    return {
        "classification": classificacao,
        "risk_score": risk_score,
        "obligations": obligations,
        "gaps": gaps,
        "action_plan": action_plan,
    }


@router.post("/avaliar")
async def avaliar(dados: AvaliacaoIn):
    """Sprint 4 equivalente do NR1: motor real + PDF. IA só redige o resumo executivo."""
    resultado = _avaliar_respostas(dados.respostas)

    settings = Settings()
    deepseek = DeepSeekClient(settings)
    resumo_prompt = (
        f"Company: {dados.company}\nSOC2 readiness score: {resultado['risk_score']}/100\n"
        f"Classification: {resultado['classification']}\nGaps: {resultado['gaps']}\n"
        "Write a 2-3 sentence executive summary explaining this result in plain business language."
    )
    resumo = await asyncio.to_thread(
        deepseek.chat, "You are a SOC2 audit readiness advisor.", resumo_prompt
    )
    resultado["classification_reasoning"] = resumo

    from fastapi.responses import StreamingResponse
    marca_dagua = not dados.licenca_premium
    pdf_buf = gerar_pdf_relatorio("SOC 2 Readiness Report", dados.company, resultado)
    if not dados.licenca_premium:
        return {
            "preview": resultado,
            "message": "Relatório completo com marca d'água — desbloqueie a versão premium para baixar sem marca d'água.",
            "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08",
        }
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": 'attachment; filename="SOC2_Readiness_Report.pdf"'})


@router.post("/readiness-assessment")
async def soc2_assessment_legacy(data: dict):
    """Compatibilidade — fluxo antigo em texto livre, sem catálogo."""
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = f"Company: {data.get('company', '')}\nCurrent controls: {data.get('current_controls', 'unknown')}"
    response = await asyncio.to_thread(
        deepseek.chat, "You are a SOC2 audit preparation specialist.", prompt
    )
    return {"assessment": response, "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08"}

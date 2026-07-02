"""Global ISO27001 Copilot — questionário estruturado (catálogo real Anexo A) ->
motor de gap relacional -> PDF com paywall free/premium. Mesma arquitetura do NR1/SOC2.

Fonte do catálogo: ISO/IEC 27001:2022, Anexo A (93 controles em 4 temas:
Organizacional 5.1-5.37, Pessoas 6.1-6.8, Físico 7.1-7.14, Tecnológico 8.1-8.34).
"""
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents._copilot_common import gerar_pdf_relatorio

router = APIRouter(prefix="/api/iso27001", tags=["iso27001"])

# Catálogo real — Parte 01: 16 controles representativos dos 4 temas do Anexo A.
CATALOGO_ISO27001 = [
    {"id": "5.1", "categoria": "Organizacional", "nome": "Policies for Information Security",
     "pergunta": "Existe política de segurança da informação aprovada pela direção e comunicada?", "obrigatorio": True},
    {"id": "5.2", "categoria": "Organizacional", "nome": "Information Security Roles and Responsibilities",
     "pergunta": "Papéis e responsabilidades de segurança da informação estão claramente definidos?", "obrigatorio": True},
    {"id": "5.3", "categoria": "Organizacional", "nome": "Segregation of Duties",
     "pergunta": "Existe segregação de funções para tarefas conflitantes (ex: quem aprova ≠ quem executa)?", "obrigatorio": True},
    {"id": "5.15", "categoria": "Organizacional", "nome": "Access Control",
     "pergunta": "Existe política formal de controle de acesso baseada em papéis/necessidade?", "obrigatorio": True},
    {"id": "5.23", "categoria": "Organizacional", "nome": "Information Security for Use of Cloud Services",
     "pergunta": "Existe avaliação formal de segurança dos provedores de nuvem utilizados?", "obrigatorio": True},
    {"id": "5.24", "categoria": "Organizacional", "nome": "Information Security Incident Management Planning",
     "pergunta": "Existe plano documentado de resposta a incidentes de segurança?", "obrigatorio": True},
    {"id": "6.3", "categoria": "Pessoas", "nome": "Information Security Awareness, Education and Training",
     "pergunta": "Funcionários recebem treinamento periódico de conscientização em segurança?", "obrigatorio": True},
    {"id": "6.7", "categoria": "Pessoas", "nome": "Remote Working",
     "pergunta": "Existe política formal para trabalho remoto com controles de segurança específicos?", "obrigatorio": False},
    {"id": "7.1", "categoria": "Físico", "nome": "Physical Security Perimeters",
     "pergunta": "Existem perímetros de segurança física definidos e protegidos nas instalações?", "obrigatorio": True},
    {"id": "7.2", "categoria": "Físico", "nome": "Physical Entry",
     "pergunta": "O acesso físico a áreas seguras é controlado (crachá, fechadura, registro)?", "obrigatorio": True},
    {"id": "8.7", "categoria": "Tecnológico", "nome": "Protection Against Malware",
     "pergunta": "Existe proteção antimalware ativa em todos os endpoints e servidores?", "obrigatorio": True},
    {"id": "8.8", "categoria": "Tecnológico", "nome": "Management of Technical Vulnerabilities",
     "pergunta": "Existe processo de identificação e correção de vulnerabilidades técnicas (patch management)?", "obrigatorio": True},
    {"id": "8.13", "categoria": "Tecnológico", "nome": "Information Backup",
     "pergunta": "Existe backup regular com teste de restauração documentado?", "obrigatorio": True},
    {"id": "8.15", "categoria": "Tecnológico", "nome": "Logging",
     "pergunta": "Eventos de sistema são registrados em log e retidos por período definido?", "obrigatorio": True},
    {"id": "8.16", "categoria": "Tecnológico", "nome": "Monitoring Activities",
     "pergunta": "Existe monitoramento ativo de rede/sistemas para detectar comportamento anômalo?", "obrigatorio": True},
    {"id": "8.24", "categoria": "Tecnológico", "nome": "Use of Cryptography",
     "pergunta": "Dados sensíveis são criptografados em repouso e em trânsito?", "obrigatorio": True},
]

RECOMENDACOES = {
    "5.1": "Formalize e publique a política de segurança da informação, aprovada pela direção.",
    "5.2": "Documente matriz RACI de papéis e responsabilidades de segurança da informação.",
    "5.3": "Implemente segregação entre quem solicita, aprova e executa mudanças/acessos críticos.",
    "5.15": "Formalize política de controle de acesso baseada em papéis (RBAC).",
    "5.23": "Realize due diligence de segurança formal para cada provedor de nuvem contratado.",
    "5.24": "Documente plano de resposta a incidentes com papéis, escalonamento e comunicação.",
    "6.3": "Implemente programa de treinamento de conscientização, no mínimo anual.",
    "6.7": "Documente política de trabalho remoto com requisitos de VPN/dispositivo/rede.",
    "7.1": "Defina e proteja fisicamente o perímetro das instalações com controles de acesso.",
    "7.2": "Implemente controle de entrada física (crachá, biometria, registro de visitantes).",
    "8.7": "Instale e mantenha atualizada solução antimalware em todos os dispositivos.",
    "8.8": "Implemente scan de vulnerabilidades periódico com SLA de correção definido.",
    "8.13": "Configure backup automatizado com teste de restauração trimestral.",
    "8.15": "Centralize logs de sistema com retenção mínima de 90 dias.",
    "8.16": "Implemente ferramenta de monitoramento/SIEM com alertas configurados.",
    "8.24": "Implemente criptografia (TLS em trânsito, AES-256 em repouso) para dados sensíveis.",
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
    return {"framework": "ISO/IEC 27001:2022 (Anexo A)", "perguntas": CATALOGO_ISO27001}


def _avaliar_respostas(respostas: list[RespostaItem]) -> dict:
    catalogo_por_id = {c["id"]: c for c in CATALOGO_ISO27001}
    respostas_por_id = {r.controle_id: r.status for r in respostas}

    obligations, gaps, action_plan = [], [], []
    pontos_totais = pontos_obtidos = 0

    for controle in CATALOGO_ISO27001:
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
        classificacao = "Certification Ready"
    elif risk_score >= 60:
        classificacao = "Partial Compliance"
    else:
        classificacao = "Not Ready"

    return {"classification": classificacao, "risk_score": risk_score,
            "obligations": obligations, "gaps": gaps, "action_plan": action_plan}


@router.post("/avaliar")
async def avaliar(dados: AvaliacaoIn):
    resultado = _avaliar_respostas(dados.respostas)

    settings = Settings()
    deepseek = DeepSeekClient(settings)
    resumo_prompt = (
        f"Company: {dados.company}\nISO 27001 readiness score: {resultado['risk_score']}/100\n"
        f"Classification: {resultado['classification']}\nGaps: {resultado['gaps']}\n"
        "Write a 2-3 sentence executive summary in plain business language."
    )
    resultado["classification_reasoning"] = await asyncio.to_thread(
        deepseek.chat, "You are an ISO 27001 certification readiness advisor.", resumo_prompt
    )

    if not dados.licenca_premium:
        return {
            "preview": resultado,
            "message": "Relatório completo com marca d'água — desbloqueie a versão premium para baixar sem marca d'água.",
            "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08",
        }
    pdf_buf = gerar_pdf_relatorio("ISO/IEC 27001:2022 Gap Analysis Report", dados.company, resultado)
    return StreamingResponse(pdf_buf, media_type="application/pdf",
                              headers={"Content-Disposition": 'attachment; filename="ISO27001_Gap_Report.pdf"'})


@router.post("/gap-analysis")
async def iso27001_gap_legacy(data: dict):
    """Compatibilidade — fluxo antigo em texto livre."""
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    prompt = f"Company: {data.get('company', '')}\nCurrent security controls: {data.get('current_controls', 'basic')}"
    response = await asyncio.to_thread(
        deepseek.chat, "You are an ISO 27001 ISMS specialist.", prompt
    )
    return {"gap_analysis": response, "checkout_url": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08"}

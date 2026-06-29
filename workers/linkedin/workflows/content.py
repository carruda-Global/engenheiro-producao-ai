import logging
from datetime import datetime
from integrations.linkedin import LinkedInIntegration
from integrations.linkedin.config import LinkedInConfig

logger = logging.getLogger(__name__)

CALENDARIO = {
    0: {
        "agente": "NR-1 Psicossocial",
        "urgencia": "Multa ativa desde maio/2025 — sua empresa esta em risco",
        "gancho": "Portaria MTE 1.419/2024 ja esta sendo fiscalizada. Empresas sem inventario FRPRT estao sendo notificadas.",
        "solucao": "O agente NR-1 faz o inventario de riscos psicossociais, plano de acao e relatorios em 48h.",
        "cta": "Compliance Essencial R$ 590",
        "utm": "nr1",
    },
    1: {
        "agente": "LGPD Operacional",
        "urgencia": "ANPD autuou mais de 50 empresas em 2025 — voc tem RoPA?",
        "gancho": "A ANPD esta fiscalizando ativamente. Multas podem chegar a R$ 50 milhoes por infracao.",
        "solucao": "O agente LGPD mapeia dados, gera RoPA e mantem conformidade continua com a ANPD.",
        "cta": "Compliance Essencial R$ 590",
        "utm": "lgpd",
    },
    2: {
        "agente": "CBS/IBS Tributario",
        "urgencia": "Janela 2026-2027 fechando — seu NCM esta classificado?",
        "gancho": "A LC 214/2025 entra em vigor e sua empresa precisa classificar todos os produtos por NCM e gerar DeRE.",
        "solucao": "O agente CBS/IBS classifica NCM automaticamente, simula impacto fiscal e gera DeRE.",
        "cta": "Tributario R$ 390",
        "utm": "tributario",
    },
    3: {
        "agente": "ESG IFRS S1/S2",
        "urgencia": "Seu fornecedor europeu ja pediu relatorio de carbono?",
        "gancho": "IFRS S1/S2 exigem relatorios ESG auditaveis. Sem eles, voce perde contratos internacionais.",
        "solucao": "O agente ESG gera diagnostico, relatorios IFRS e calcula carbono Escopo 1/2.",
        "cta": "ESG+Carbono R$ 2.490",
        "utm": "esg",
    },
    4: {
        "agente": "Micro-agente M1",
        "urgencia": "Diagnostico NR-1 por R$ 99 — resultado em 48h",
        "gancho": "Comece com um diagnostico rapido de riscos psicossociais por apenas R$ 99. Sem compromisso.",
        "solucao": "O M1 Diagnostico Rapido NR-1 avalia sua empresa e entrega relatorio preliminar em 48h.",
        "cta": "Porta de entrada R$ 99",
        "utm": "micro-m1",
    },
}


def gerar_post_calendario(dia_semana: int | None = None) -> tuple[str, str, str]:
    if dia_semana is None:
        dia_semana = datetime.now().weekday()
    if dia_semana > 4:
        dia_semana = 0

    tema = CALENDARIO[dia_semana]
    post = (
        f"{tema['urgencia']}\n\n"
        f"{tema['gancho']}\n\n"
        f"{tema['solucao']}\n\n"
        f"Resultado em 48h\n"
        f"Sem implantacao\n"
        f"Trial 15 dias gratis\n\n"
        f"Link nos comentarios"
    )
    comentario = (
        f"https://global-engenharia.com/ecosystem"
        f"?utm_source=linkedin"
        f"&utm_medium=organic"
        f"&utm_campaign={tema['utm']}"
        f"&utm_content=post-{['seg','ter','qua','qui','sex'][dia_semana]}"
    )
    return post, comentario, tema["cta"]


async def run_content_workflow(linkedin: LinkedInIntegration | None = None) -> dict:
    if not linkedin:
        li_config = LinkedInConfig()
        linkedin = LinkedInIntegration(config=li_config)
        await linkedin.initialize()

    post_text, comment_text, cta = gerar_post_calendario()
    result = await linkedin.tools.create_post(text=post_text)

    if "error" not in result and result.get("post_id"):
        await linkedin.tools.create_comment(post_id=result["post_id"], text=comment_text)

    await linkedin.shutdown()

    success = "error" not in result
    return {
        "workflow": "Geracao de Conteudo LinkedIn",
        "tema": CALENDARIO.get(datetime.now().weekday(), {}).get("agente", ""),
        "cta": cta,
        "published": success,
        "post_url": result.get("url", ""),
        "completed_at": datetime.utcnow().isoformat(),
    }

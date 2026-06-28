import logging
from datetime import datetime
from integrations.linkedin import LinkedInIntegration
from integrations.linkedin.config import LinkedInConfig

logger = logging.getLogger(__name__)

TOPICS = [
    "NR-1 Psicossocial: como adequar sua empresa a Portaria MTE 1.419/2024",
    "LGPD para PMEs: 5 passos para evitar multas de ate R$ 50 milhoes",
    "ESG na pratica: IFRS S1/S2 e porque sua empresa precisa se preparar",
    "59 agentes de IA para automatizar compliance da sua empresa",
    "LinkedIn Sales: como usar IA para prospectar clientes B2B",
    "Canal de Denuncias: obrigatorio para empresas com mais de 100 funcionarios",
    "Igualdade Salarial: como fazer o relatorio do MTE em 48h",
    "Inventario de Carbono: sua empresa precisa em 2026",
    "Microsoft + IA: 6 agentes integrados ao Teams e SharePoint",
    "Dynamics 365 com IA: automate seu CRM sem programacao",
]


async def run_content_workflow(linkedin: LinkedInIntegration | None = None) -> dict:
    if not linkedin:
        li_config = LinkedInConfig()
        linkedin = LinkedInIntegration(config=li_config)
        await linkedin.initialize()

    week = datetime.now().isocalendar()[1]
    topic = TOPICS[week % len(TOPICS)]

    post = (
        f"{topic}\n\n"
        f"Resultado em 48h. Trial gratuito de 15 dias.\n\n"
        f"https://global-engenharia.com/ecosystem\n\n"
        f"#IA #Compliance #LGPD #NR1 #ESG #Inovacao #AION"
    )

    result = await linkedin.tools.create_post(text=post)
    await linkedin.shutdown()

    success = "error" not in result
    return {
        "workflow": "Geracao de Conteudo LinkedIn",
        "topic": topic,
        "published": success,
        "post_url": result.get("url", ""),
        "completed_at": datetime.utcnow().isoformat(),
    }

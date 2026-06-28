import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

OUTREACH_TEMPLATES = {
    "default": {
        "subject": "Conectando ideias sobre {industry}",
        "steps": [
            {
                "day": 0,
                "channel": "linkedin",
                "subject": "Conexão",
                "template": (
                    "Olá {name}, vi seu perfil e seu trabalho com {industry} "
                    "na {company}. Tenho uma ideia que pode gerar "
                    "{value_proposition}. Vamos conversar?"
                ),
            },
            {
                "day": 3,
                "channel": "email",
                "subject": "Ideia para {company}",
                "template": (
                    "Oi {name}, tudo bem?\n\n"
                    "Vi seu trabalho com {industry} na {company} e pensei "
                    "em algo que pode ajudar.\n\n"
                    "{value_proposition}\n\n"
                    "Tem 15 minutos para um café virtual esta semana?"
                ),
            },
            {
                "day": 7,
                "channel": "linkedin",
                "subject": "Follow-up",
                "template": (
                    "Oi {name}, só lembrando da minha mensagem anterior. "
                    "Acredito que podemos ajudar {company} a "
                    "{value_proposition}. Vale um papo rápido?"
                ),
            },
        ],
    },
    "regulatory": {
        "subject": "Adequação regulatória para {industry}",
        "steps": [
            {
                "day": 0,
                "channel": "linkedin",
                "subject": "Regulatório {industry}",
                "template": (
                    "Olá {name}, notei que {company} atua em {industry}. "
                    "Com as novas exigências regulatórias, desenvolvemos "
                    "uma solução que pode ajudar na adequação contínua. "
                    "Posso te mostrar?"
                ),
            },
            {
                "day": 4,
                "channel": "email",
                "subject": "Adequação {industry} - {company}",
                "template": (
                    "Oi {name},\n\n"
                    "Para empresas de {industry}, a conformidade regulatória "
                    "é um desafio constante. Nossa plataforma automatiza "
                    "todo o processo com agentes de IA especializados.\n\n"
                    "{value_proposition}\n\n"
                    "Agenda uma demo?"
                ),
            },
        ],
    },
    "cross_sell": {
        "subject": "Otimizando sua experiência",
        "steps": [
            {
                "day": 0,
                "channel": "email",
                "subject": "Novidade para sua empresa",
                "template": (
                    "Oi {name}, tudo bem?\n\n"
                    "Notei que sua empresa utiliza nossos serviços. "
                    "Temos um novo agente que pode ajudar com "
                    "{value_proposition}.\n\n"
                    "Clientes do seu segmento estão economizando "
                    "até 40% de tempo.\n\n"
                    "Vamos agendar uma conversa?"
                ),
            },
        ],
    },
}


def select_template(lead: dict) -> str:
    industry = (lead.get("industry") or "").lower()
    summary = (lead.get("summary") or "").lower()

    regulatory_keywords = ["lgpd", "regulatory", "compliance", "nr-", "norma"]
    if any(kw in summary for kw in regulatory_keywords):
        return "regulatory"
    if any(kw in industry for kw in ["regulatory", "compliance", "healthcare", "financial"]):
        return "regulatory"

    return "default"


def generate_outreach_sequence(
    lead: dict,
    value_proposition: str = "otimizar processos com IA especializada",
    template_name: str | None = None,
) -> list[dict]:
    template_name = template_name or select_template(lead)
    template = OUTREACH_TEMPLATES.get(template_name, OUTREACH_TEMPLATES["default"])

    fmt = {
        "name": lead.get("name", "?"),
        "company": lead.get("company", "sua empresa"),
        "industry": lead.get("industry", "mercado"),
        "value_proposition": value_proposition,
    }
    steps = []
    for step in template["steps"]:
        content = step["template"].format(**fmt)
        subject = step["subject"].format(**fmt)
        scheduled_at = datetime.utcnow() + timedelta(days=step["day"])
        steps.append({
            "step_number": step["day"],
            "channel": step["channel"],
            "subject": subject,
            "content": content,
            "scheduled_at": scheduled_at.isoformat(),
            "status": "pending",
        })

    return steps


def generate_linkedin_message(lead: dict, value_proposition: str = "") -> str:
    name = lead.get("name", "?")
    company = lead.get("company", "sua empresa")
    industry = lead.get("industry", "mercado")
    vp = value_proposition or "otimizar processos com IA"

    return (
        f"Olá {name}, vi seu perfil e o trabalho da {company} "
        f"no setor de {industry}. Desenvolvemos agentes de IA "
        f"que podem ajudar {vp}. "
        f"Topa um papo rápido de 10 minutos?"
    )


def generate_email_content(lead: dict, value_proposition: str = "") -> dict:
    template_name = select_template(lead)
    template = OUTREACH_TEMPLATES.get(template_name, OUTREACH_TEMPLATES["default"])
    step = template["steps"][1] if len(template["steps"]) > 1 else template["steps"][0]

    fmt = {
        "name": lead.get("name", "?"),
        "company": lead.get("company", "sua empresa"),
        "industry": lead.get("industry", "mercado"),
        "value_proposition": value_proposition or "otimizar processos com IA especializada",
    }

    return {
        "to": lead.get("email", ""),
        "subject": step["subject"].format(**fmt),
        "content": step["template"].format(**fmt),
    }

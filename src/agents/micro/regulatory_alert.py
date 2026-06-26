async def run(context: dict) -> dict:
    return {
        "agent": "regulatory_alert",
        "parent": "regulatory_watch",
        "output": "Email/Teams alert quando a norma monitorada e atualizada. Monitore todas as obrigacoes regulatorias da sua empresa",
        "upsell_trigger": "regulatory_watch",
        "upsell_message": "Monitore todas as obrigacoes regulatorias da sua empresa",
    }

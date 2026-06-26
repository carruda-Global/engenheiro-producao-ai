async def run(context: dict) -> dict:
    return {
        "agent": "code_reviewer",
        "parent": "software_engineering",
        "output": "Comentarios de revisao no PR com sugestoes de melhoria. Eleve a qualidade arquitetural e gere documentacao automatica",
        "upsell_trigger": "software_engineering",
        "upsell_message": "Eleve a qualidade arquitetural e gere documentacao automatica",
    }

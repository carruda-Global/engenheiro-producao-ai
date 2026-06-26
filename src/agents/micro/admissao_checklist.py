async def run(context: dict) -> dict:
    return {
        "agent": "admissao_checklist",
        "parent": "onboarding_funcionarios",
        "output": "Checklist digital com status por item e responsavel. Automatize provisionamento de acesso para novos colaboradores",
        "upsell_trigger": "onboarding_funcionarios",
        "upsell_message": "Automatize provisionamento de acesso para novos colaboradores",
    }

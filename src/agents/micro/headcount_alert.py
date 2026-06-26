async def run(context: dict) -> dict:
    return {
        "agent": "headcount_alert",
        "parent": "workforce_orchestrator",
        "output": "Alerta semanal com equipe sobrecarregada e sugestao de realocacao. Automatize distribuicao de tarefas e gestao de alocacao",
        "upsell_trigger": "workforce_orchestrator",
        "upsell_message": "Automatize distribuicao de tarefas e gestao de alocacao",
    }

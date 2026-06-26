async def run(context: dict) -> dict:
    return {
        "agent": "expense_anomaly",
        "parent": "dynamics_finance",
        "output": "Alerta de anomalias com valor, categoria e responsavel. Automatize conciliacao e fechamento mensal completo",
        "upsell_trigger": "dynamics_finance",
        "upsell_message": "Automatize conciliacao e fechamento mensal completo",
    }

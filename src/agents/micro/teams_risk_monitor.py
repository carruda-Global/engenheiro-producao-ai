async def run(context: dict) -> dict:
    return {
        "agent": "teams_risk_monitor",
        "parent": "channel_agent",
        "output": "Alertas em tempo real no canal. Risco detectado em outros canais - expanda o monitoramento",
        "upsell_trigger": "channel_agent",
        "upsell_message": "Risco detectado em outros canais - expanda o monitoramento",
    }

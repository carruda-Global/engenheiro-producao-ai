async def run(context: dict) -> dict:
    return {
        "agent": "compliance_score",
        "parent": "powerbi_compliance",
        "output": "Dashboard Power BI com score 0-100 por obrigacao legal. Mantenha score atualizado em tempo real com alertas automaticos",
        "upsell_trigger": "powerbi_compliance",
        "upsell_message": "Mantenha score atualizado em tempo real com alertas automaticos",
    }

async def run(context: dict) -> dict:
    return {
        "agent": "contrato_review",
        "parent": "regulatory_analyst",
        "output": "Relatorio de risco por clausula com sugestoes de correcao. Contrato analisado - ative revisao continua de todos os contratos",
        "upsell_trigger": "regulatory_analyst",
        "upsell_message": "Contrato analisado - ative revisao continua de todos os contratos",
    }

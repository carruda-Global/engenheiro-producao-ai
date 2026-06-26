async def run(context: dict) -> dict:
    return {
        "agent": "lead_qualifier",
        "parent": "sales_agent",
        "output": "Score de qualificacao + proxima acao recomendada. Automatize proposta, desconto e upsell para leads qualificados",
        "upsell_trigger": "sales_agent",
        "upsell_message": "Automatize proposta, desconto e upsell para leads qualificados",
    }

async def run(context: dict) -> dict:
    return {
        "agent": "sales_pipeline_checker",
        "parent": "dynamics_sales",
        "output": "Relatorio semanal com deals em risco e acao recomendada. Automatize follow-ups e qualificacao de leads",
        "upsell_trigger": "dynamics_sales",
        "upsell_message": "Automatize follow-ups e qualificacao de leads",
    }

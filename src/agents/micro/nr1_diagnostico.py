async def run(context: dict) -> dict:
    return {
        "agent": "nr1_diagnostico_rapido",
        "parent": "nr1_psicossocial",
        "output": "Diagnostico rapido NR-1 realizado. Diagnostico concluido - gere seu plano de acao completo",
        "upsell_trigger": "nr1_psicossocial",
        "upsell_message": "Diagnostico concluido - gere seu plano de acao completo",
    }

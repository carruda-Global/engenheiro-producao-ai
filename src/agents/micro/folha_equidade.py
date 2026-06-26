async def run(context: dict) -> dict:
    return {
        "agent": "folha_equidade",
        "parent": "igualdade_salarial",
        "output": "Dashboard de equidade com % de gap por cargo. Gap identificado - gere o relatorio MTE e plano de correcao",
        "upsell_trigger": "igualdade_salarial",
        "upsell_message": "Gap identificado - gere o relatorio MTE e plano de correcao",
    }

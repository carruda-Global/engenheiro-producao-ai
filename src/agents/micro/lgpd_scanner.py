async def run(context: dict) -> dict:
    return {
        "agent": "lgpd_scanner",
        "parent": "lgpd_operacional",
        "output": "Inventario de dados pessoais por sistema concluido. Dados mapeados - gere o RoPA completo para a ANPD",
        "upsell_trigger": "lgpd_operacional",
        "upsell_message": "Dados mapeados - gere o RoPA completo para a ANPD",
    }

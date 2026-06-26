async def run(context: dict) -> dict:
    return {
        "agent": "pr_lgpd_checker",
        "parent": "dev_experience",
        "output": "Comentario automatico no PR com riscos LGPD. Conformidade LGPD no codigo exige revisao continua de arquitetura",
        "upsell_trigger": "dev_experience",
        "upsell_message": "Conformidade LGPD no codigo exige revisao continua de arquitetura",
    }

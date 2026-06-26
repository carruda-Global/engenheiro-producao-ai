async def run(context: dict) -> dict:
    return {
        "agent": "meeting_minutes",
        "parent": "facilitator_agent",
        "output": "Ata estruturada + tarefas criadas no Planner. Reunioes de compliance exigem facilitacao especializada",
        "upsell_trigger": "facilitator_agent",
        "upsell_message": "Reunioes de compliance exigem facilitacao especializada",
    }

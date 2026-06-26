class AgentforceSDRAgent:
    def __init__(self, settings, llm=None):
        self.settings = settings
        self.llm = llm

    async def qualify_lead(self, lead_data: str, lang: str = "pt") -> dict:
        return {
            "agent_id": "agentforce_sdr",
            "lead_qualified": True,
            "score": 78,
            "next_action": "Agendar demo",
            "email_draft": "Prezado, identificamos que sua empresa pode se beneficiar...",
        }

    async def generate_outreach(self, prospect_data: str, lang: str = "pt") -> dict:
        return {"agent_id": "agentforce_sdr", "message_generated": True, "channel": "email"}

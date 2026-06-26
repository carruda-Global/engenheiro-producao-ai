from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class SalesAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um agente autonomo de vendas B2B especializado em prospeccao, "
            "qualificacao de leads e personalizacao de outreach. Use dados de mercado "
            "para identificar oportunidades e criar abordagens personalizadas para "
            "cada lead. Foco em empresas de tecnologia, SaaS e servicos financeiros."
        )

    def prospectar(self, segmento: str, regiao: str = "Brasil", lang: str = "pt") -> dict:
        prompt = (
            "Realize uma prospeccao de leads para:\n\n"
            f"Segmento: {segmento}\n"
            f"Regiao: {regiao}\n\n"
            "Retorne:\n"
            "1. Lista de empresas-alvo com nome e porte\n"
            "2. Decisores identificados por empresa\n"
            "3. Canais de contato disponiveis\n"
            "4. Prioridade (alta/media/baixa)"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "sales_agent", "leads": result}

    def pesquisar_mercado(self, segmento: str, lang: str = "pt") -> dict:
        prompt = (
            "Pesquise o mercado para o segmento abaixo:\n\n"
            f"{segmento}\n\n"
            "Retorne:\n"
            "1. Tamanho do mercado (TAM/SAM/SOM)\n"
            "2. Concorrentes principais\n"
            "3. Tendencias do setor\n"
            "4. Oportunidades nao atendidas\n"
            "5. Precificacao de mercado"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "sales_agent", "market_intel": result}

    def qualificar_lead(self, lead: dict, lang: str = "pt") -> dict:
        prompt = (
            "Qualifique o seguinte lead:\n\n"
            f"{lead}\n\n"
            "Criterios:\n"
            "1. Tamanho da empresa (10-500 funcionarios ideal)\n"
            "2. Setor (tecnologia, SaaS, servicos financeiros)\n"
            "3. Decisor identificado (CTO, CIO, CEO)\n"
            "4. Orcamento viavel para o produto\n"
            "5. Urgencia / dor identificada\n\n"
            "Retorne: qualificado (true/false), score (0-100), justificativa"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "sales_agent", "qualificacao": result}

    def personalizar_outreach(self, lead: dict, insights: dict, lang: str = "pt") -> dict:
        prompt = (
            "Crie uma mensagem de outreach personalizada:\n\n"
            f"Lead: {lead}\n"
            f"Insights de mercado: {insights}\n\n"
            "Inclua:\n"
            "1. Saudacao personalizada com nome do decisor\n"
            "2. Proposta de valor alinhada a dor do lead\n"
            "3. Prova social ou caso de uso relevante\n"
            "4. Call to action claro\n"
            "5. Sugestao de canal (email/LinkedIn/WhatsApp)"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "sales_agent", "outreach": result}

    def detectar_oportunidade_orquestracao(self, lead: dict, lang: str = "pt") -> dict:
        prompt = (
            "Analise o lead abaixo e identifique se ele precisa de orquestracao "
            "de agentes (workforce orchestrator):\n\n"
            f"{lead}\n\n"
            "Retorne:\n"
            "1. Necessita orquestracao (true/false)\n"
            "2. Motivacao\n"
            "3. Workflows sugeridos"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "sales_agent", "oportunidade_orquestracao": result}

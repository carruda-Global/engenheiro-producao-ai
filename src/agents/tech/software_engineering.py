from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class SoftwareEngineeringAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um engenheiro de software senior especializado em desenvolvimento "
            "de agentes de IA, automacao e integracoes. Sua funcao e analisar "
            "requisitos, gerar codigo, revisar qualidade e documentar APIs. "
            "Trabalhe com boas praticas: clean code, testes, seguranca e performance."
        )

    def analisar_requisitos(self, descricao: str, lang: str = "pt") -> dict:
        prompt = (
            "Analise os requisitos abaixo e produza uma especificacao tecnica:\n\n"
            f"{descricao}\n\n"
            "Retorne:\n"
            "1. Arquitetura recomendada\n"
            "2. Componentes necessarios\n"
            "3. Dependencias e integracoes\n"
            "4. Estimativa de esforco\n"
            "5. Riscos tecnicos"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "software_engineering", "especificacao": result}

    def gerar_codigo(self, especificacao: str, linguagem: str = "python", lang: str = "pt") -> dict:
        prompt = (
            "Com base na especificacao abaixo, gere o codigo completo:\n\n"
            f"{especificacao}\n\n"
            f"Linguagem: {linguagem}\n\n"
            "Inclua:\n"
            "1. Estrutura de diretorios\n"
            "2. Codigo fonte completo\n"
            "3. Testes unitarios\n"
            "4. Documentacao basica\n"
            "5. Dockerfile se aplicavel"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "software_engineering", "codigo": result}

    def revisar_codigo(self, codigo: str, lang: str = "pt") -> dict:
        prompt = (
            "Revise o codigo abaixo e identifique:\n\n"
            f"{codigo}\n\n"
            "Retorne:\n"
            "1. Problemas de seguranca\n"
            "2. Violacoes de boas praticas\n"
            "3. Oportunidades de performance\n"
            "4. Sugestoes de melhoria\n"
            "5. Score de qualidade (0-100)"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "software_engineering", "revisao": result}

    def detectar_oportunidade_vendas(self, contexto: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base no contexto abaixo, identifique se ha necessidade "
            "de acionar o agente de vendas:\n\n"
            f"{contexto}\n\n"
            "Retorne:\n"
            "1. Oportunidade identificada (true/false)\n"
            "2. Justificativa\n"
            "3. Dados para o agente de vendas"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "software_engineering", "oportunidade_vendas": result}

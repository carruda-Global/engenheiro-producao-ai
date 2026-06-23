from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class BIMCoordinatorAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em Coordenacao BIM com inteligencia artificial. "
            "Sua funcao e criar elementos 3D a partir de comandos de texto, "
            "detectar conflitos entre disciplinas (clash detection), realizar "
            "raciocinio espacial e validar modelos BIM contra especificacoes. "
            "Trabalhe com precisao dimensional e normas como NBR-15965."
        )

    def generate_bim_element(self, description: str, lang: str = "pt") -> dict:
        prompt = (
            "Com base na descricao abaixo, gere as especificacoes para "
            "criacao de um elemento BIM 3D:\n\n"
            f"{description}\n\n"
            "Inclua:\n"
            "1. Tipo de elemento (parede, laje, viga, pilar, etc.)\n"
            "2. Dimensoes principais (largura, altura, comprimento)\n"
            "3. Material especificado\n"
            "4. Nivel/Layer de referencia\n"
            "5. Parametros tecnicos relevantes\n"
            "6. Conflitos potenciais com outros elementos"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "bim_coordinator", "bim_element": result}

    def clash_detection(self, model_description: str, lang: str = "pt") -> str:
        prompt = (
            "Analise o modelo descrito abaixo e identifique conflitos "
            "entre as disciplinas (estrutural, hidraulico, eletrico, arquitetonico):\n\n"
            f"{model_description}\n\n"
            "Liste cada conflito com:\n"
            "1. Disciplinas envolvidas\n"
            "2. Localizacao do conflito\n"
            "3. Gravidade (alto/medio/baixo)\n"
            "4. Sugestao de resolucao"
        )
        return self.llm.chat(self.system_prompt, prompt, lang=lang)

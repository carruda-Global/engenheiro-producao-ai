from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class ComplianceAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um especialista em gestao de conformidade para "
            "construcao civil, focado em PGRS (Programa de Gerenciamento "
            "de Residuos Solidos) e PGRSS (Programa de Gerenciamento de "
            "Residuos Solidos de Saude). Sua funcao e monitorar requisitos "
            "legais, gerar documentacao de conformidade, emitir alertas "
            "sobre prazos e obrigacoes, e garantir que a obra atenda "
            "normas ambientais e regulatorias. Use normas como NBR-10004, "
            "Resolucoes CONAMA e legislacao municipal."
        )

    def check_compliance(self, project_data: str, lang: str = "pt") -> dict:
        prompt = (
            "Analise os dados do projeto abaixo e verifique a conformidade "
            "com requisitos legais e normativos:\n\n"
            f"{project_data}\n\n"
            "Para cada item, informe:\n"
            "1. Requisito aplicavel\n"
            "2. Status (conforme / nao conforme / nao aplicavel)\n"
            "3. Evidencia ou justificativa\n"
            "4. Acao corretiva se necessario\n\n"
            "Ao final, forneca um score geral de conformidade (0-100%)."
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "compliance", "compliance_report": result}

    def generate_pgrs(self, project_info: str, lang: str = "pt") -> str:
        prompt = (
            "Com base nas informacoes do projeto abaixo, gere um esboco "
            "de PGRS (Programa de Gerenciamento de Residuos Solidos):\n\n"
            f"{project_info}\n\n"
            "Inclua:\n"
            "1. Caracterizacao dos residuos gerados\n"
            "2. Classificacao conforme NBR-10004\n"
            "3. Quantificacao estimada\n"
            "4. Procedimentos de coleta e armazenamento\n"
            "5. Transporte e destinacao final\n"
            "6. Responsaveis tecnicos\n"
            "7. Cronograma de execucao"
        )
        return self.llm.chat(self.system_prompt, prompt, lang=lang)

    def monitor_deadlines(self, obligations: str, lang: str = "pt") -> str:
        prompt = (
            "Analise as obrigacoes legais e regulatorias abaixo e "
            "identifique prazos, renovacoes e alertas:\n\n"
            f"{obligations}\n\n"
            "Para cada obrigacao:\n"
            "1. Descricao\n"
            "2. Orgao regulatorio\n"
            "3. Data de vencimento\n"
            "4. Status (em dia / a vencer / vencido)\n"
            "5. Acao recomendada"
        )
        return self.llm.chat(self.system_prompt, prompt, lang=lang)

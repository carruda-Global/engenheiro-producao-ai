from src.api.deepseek_client import DeepSeekClient
from src.config import Settings


class WorkforceOrchestratorAgent:
    def __init__(self, settings: Settings, llm: DeepSeekClient):
        self.settings = settings
        self.llm = llm
        self.system_prompt = (
            "Voce e um orquestrador de workforce digital especializado em coordenar "
            "agentes de IA para workflows complexos. Sua funcao e planejar, atribuir, "
            "monitorar e otimizar a execucao de tarefas entre multiplos agentes. "
            "Garanta eficiencia, tratamento de excecoes e geracao de relatorios."
        )

    def planejar_workflow(self, tarefa: str, lang: str = "pt") -> dict:
        prompt = (
            "Planeje um workflow completo para a tarefa abaixo:\n\n"
            f"{tarefa}\n\n"
            "Retorne:\n"
            "1. Passos do workflow em sequencia\n"
            "2. Dependencias entre passos\n"
            "3. Agentes necessarios para cada passo\n"
            "4. Estimativa de tempo por passo\n"
            "5. Criterios de sucesso"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "workforce_orchestrator", "workflow": result}

    def atribuir_tarefas(self, workflow: dict, lang: str = "pt") -> dict:
        prompt = (
            "Atribua as tarefas do workflow abaixo para os agentes disponiveis:\n\n"
            f"{workflow}\n\n"
            "Agentes disponiveis:\n"
            "- software_engineering (#28): desenvolvimento de codigo\n"
            "- sales_agent (#29): prospeccao e vendas\n"
            "- workforce_orchestrator (#30): orquestracao (este agente)\n\n"
            "Retorne:\n"
            "1. Mapeamento tarefa -> agente\n"
            "2. Prioridade de cada tarefa\n"
            "3. Dependencias entre agentes\n"
            "4. Timeline estimada"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "workforce_orchestrator", "atribuicoes": result}

    def monitorar_execucao(self, tarefas: dict, lang: str = "pt") -> dict:
        prompt = (
            "Monitore a execucao das tarefas abaixo e identifique o status:\n\n"
            f"{tarefas}\n\n"
            "Retorne:\n"
            "1. Status de cada tarefa (concluida/em_andamento/falha)\n"
            "2. Alertas de atraso\n"
            "3. Bloqueios identificados\n"
            "4. Acoes corretivas recomendadas"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "workforce_orchestrator", "monitoramento": result}

    def tratar_excecoes(self, falhas: dict, lang: str = "pt") -> dict:
        prompt = (
            "Analise as falhas abaixo e proponha acoes corretivas:\n\n"
            f"{falhas}\n\n"
            "Retorne:\n"
            "1. Causa raiz de cada falha\n"
            "2. Acao corretiva recomendada\n"
            "3. Impacto no prazo geral\n"
            "4. Necessidade de escalonamento (sim/nao)"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "workforce_orchestrator", "excecoes": result}

    def gerar_relatorio(self, resultados: dict, lang: str = "pt") -> dict:
        prompt = (
            "Gere um relatorio executivo de produtividade com base nos resultados:\n\n"
            f"{resultados}\n\n"
            "Inclua:\n"
            "1. Resumo do que foi executado\n"
            "2. Metricas de performance\n"
            "3. Recomendacoes de otimizacao\n"
            "4. Proximos passos\n"
            "5. Sugestoes de novos workflows"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "workforce_orchestrator", "relatorio": result}

    def otimizar_ecossistema(self, contexto: str, lang: str = "pt") -> dict:
        prompt = (
            "Como orquestrador do workforce digital, analise o contexto abaixo "
            "e identifique oportunidades de otimizacao em todo o ecossistema "
            "de agentes:\n\n"
            f"{contexto}\n\n"
            "Retorne:\n"
            "1. Gargalos identificados\n"
            "2. Recomendacoes de otimizacao por agente\n"
            "3. Novos workflows sugeridos\n"
            "4. Impacto estimado da otimizacao\n"
            "5. Prioridade das acoes"
        )
        result = self.llm.chat(self.system_prompt, prompt, lang=lang)
        return {"agent": "workforce_orchestrator", "otimizacao": result}

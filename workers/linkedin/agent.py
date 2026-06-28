import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from integrations.linkedin import LinkedInIntegration
from integrations.linkedin.config import LinkedInConfig
from orchestrator.workflow_runner import WorkflowRunner
from workflows.content import run_content_workflow
from workflows.outreach import run_outreach_workflow
from workflows.site import get_site_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("auto-linkedin")

LIMITES_SEGUROS = {
    "posts_por_dia": 1,
    "conexoes_por_dia": 5,
    "mensagens_por_dia": 10,
    "visitas_perfil_por_dia": 15,
    "pausa_entre_acoes": 30,
    "max_erros_consecutivos": 3,
}


class AutoLinkedInAgent:
    def __init__(self):
        self.linkedin = None
        self.running = False
        self.erros_consecutivos = 0
        self.acoes_hoje = {"posts": 0, "conexoes": 0, "mensagens": 0, "visitas": 0}
        self.dia_atual = datetime.now().day

    def resetar_limites_diarios(self):
        hoje = datetime.now().day
        if hoje != self.dia_atual:
            self.acoes_hoje = {"posts": 0, "conexoes": 0, "mensagens": 0, "visitas": 0}
            self.dia_atual = hoje
            self.erros_consecutivos = 0
            logger.info("Limites diarios resetados")

    def pode_agir(self, acao: str) -> bool:
        self.resetar_limites_diarios()
        limites = {
            "post": LIMITES_SEGUROS["posts_por_dia"],
            "conexao": LIMITES_SEGUROS["conexoes_por_dia"],
            "mensagem": LIMITES_SEGUROS["mensagens_por_dia"],
            "visita": LIMITES_SEGUROS["visitas_perfil_por_dia"],
        }
        usados = {
            "post": self.acoes_hoje["posts"],
            "conexao": self.acoes_hoje["conexoes"],
            "mensagem": self.acoes_hoje["mensagens"],
            "visita": self.acoes_hoje["visitas"],
        }
        return usados.get(acao, 0) < limites.get(acao, 0)

    def registrar_acao(self, acao: str):
        if acao in self.acoes_hoje:
            self.acoes_hoje[acao] += 1

    async def start(self):
        li_config = LinkedInConfig()
        self.linkedin = LinkedInIntegration(config=li_config)
        await self.linkedin.initialize()
        self.running = True
        logger.info("=" * 50)
        logger.info("AGENTE LINKEDIN AUTOMATICO INICIADO")
        logger.info("=" * 50)

        while self.running:
            try:
                now = datetime.now()
                if self.erros_consecutivos >= LIMITES_SEGUROS["max_erros_consecutivos"]:
                    logger.warning("Muitos erros. Pausando 6h...")
                    await asyncio.sleep(21600)
                    self.erros_consecutivos = 0

                logger.info(f"\n=== CICLO {now.strftime('%d/%m/%Y %H:%M')} ===")
                logger.info(f"Acoes hoje: {self.acoes_hoje}")

                if now.weekday() == 0 and now.hour == 9 and self.pode_agir("post"):
                    result = await run_content_workflow(self.linkedin)
                    if result.get("published"):
                        self.registrar_acao("post")
                        logger.info("Post publicado!")
                    self.erros_consecutivos = 0

                if now.hour == 8:
                    runner = WorkflowRunner(linkedin=self.linkedin)
                    try:
                        result = await runner.run_workflow("linkedin")
                        logger.info(f"Prospeccao: {result.get('steps', 0)} steps")
                        self.erros_consecutivos = 0
                    except Exception as e:
                        self.erros_consecutivos += 1
                        logger.error(f"Erro: {e}")

                if now.hour in [10, 14] and self.pode_agir("conexao"):
                    try:
                        result = await run_outreach_workflow()
                        if result.get("leads_processed", 0) > 0:
                            self.registrar_acao("conexao")
                            logger.info(f"Outreach: {result['leads_processed']} leads")
                        self.erros_consecutivos = 0
                    except Exception as e:
                        self.erros_consecutivos += 1
                        logger.error(f"Erro: {e}")

                try:
                    metrics = await get_site_metrics()
                    logger.info(f"Metricas: {metrics.get('total_leads', 0)} leads")
                except Exception as e:
                    logger.warning(f"Erro metricas: {e}")

                logger.info(f"Aguardando 1h...")
                await asyncio.sleep(3600)

            except Exception as e:
                self.erros_consecutivos += 1
                logger.error(f"Erro fatal: {e}")
                await asyncio.sleep(3600)

    async def stop(self):
        self.running = False
        if self.linkedin:
            await self.linkedin.shutdown()


async def main():
    agent = AutoLinkedInAgent()
    try:
        await agent.start()
    except KeyboardInterrupt:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())

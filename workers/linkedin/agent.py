import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from integrations.linkedin import LinkedInIntegration
from integrations.linkedin.config import LinkedInConfig
from workflows.content import run_content_workflow

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("auto-linkedin")


class AutoLinkedInAgent:
    def __init__(self):
        self.linkedin = None
        self.running = False
        self.erros = 0
        self.posts_hoje = 0
        self.dia_atual = datetime.now().day

    def resetar(self):
        hoje = datetime.now().day
        if hoje != self.dia_atual:
            self.posts_hoje = 0
            self.dia_atual = hoje
            self.erros = 0

    def pode_postar(self):
        self.resetar()
        return self.posts_hoje < 1 and datetime.now().weekday() < 5

    async def postar(self):
        if not self.pode_postar():
            return

        result = await run_content_workflow(self.linkedin)
        if result.get("published"):
            self.posts_hoje += 1
            self.erros = 0
            logger.info(f"Post publicado: {result.get('tema','?')} - {result.get('post_url','')}")

    async def start(self):
        li_config = LinkedInConfig()
        self.linkedin = LinkedInIntegration(config=li_config)
        await self.linkedin.initialize()
        self.running = True

        logger.info("=" * 50)
        logger.info("  AGENTE LINKEDIN AUTOMATICO - RENDER")
        logger.info("  Posta ao iniciar se ainda nao postou hoje")
        logger.info("  Seg: NR-1 | Ter: LGPD | Qua: CBS/IBS | Qui: ESG | Sex: M1")
        logger.info("=" * 50)

        await self.postar()

        while self.running:
            try:
                if self.erros >= 3:
                    logger.warning("Muitos erros. Pausando 6h...")
                    await asyncio.sleep(21600)
                    self.erros = 0

                logger.info(f"Ciclo {datetime.now().strftime('%d/%m/%Y %H:%M')} | posts_hoje: {self.posts_hoje} | erros: {self.erros}")
                await self.postar()
                await asyncio.sleep(1800)

            except Exception as e:
                self.erros += 1
                logger.error(f"Erro fatal: {e}")
                await asyncio.sleep(1800)

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

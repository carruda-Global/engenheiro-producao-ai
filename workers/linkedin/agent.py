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

HORARIOS = [8, 12, 17]
TIPOS = ["calendario", "news", "dica"]


class AutoLinkedInAgent:
    def __init__(self):
        self.linkedin = None
        self.running = False
        self.erros = 0
        self.posts_hoje = {"total": 0, "calendario": False, "news": False, "dica": False}
        self.dia_atual = datetime.now().day
        self.indices = {"news": datetime.now().day, "dica": datetime.now().day + 5}

    def resetar(self):
        hoje = datetime.now().day
        if hoje != self.dia_atual:
            self.posts_hoje = {"total": 0, "calendario": False, "news": False, "dica": False}
            self.dia_atual = hoje
            self.indices["news"] = hoje
            self.indices["dica"] = hoje + 5
            self.erros = 0

    def dia_util(self):
        return datetime.now().weekday() < 5

    def tipos_pendentes(self):
        self.resetar()
        if not self.dia_util():
            return []
        return [t for t in TIPOS if not self.posts_hoje[t]]

    async def postar(self, tipo: str):
        indice = self.indices.get(tipo, -1)
        result = await run_content_workflow(self.linkedin, tipo=tipo, indice=indice)
        if result.get("published"):
            self.posts_hoje[tipo] = True
            self.posts_hoje["total"] += 1
            self.erros = 0
            logger.info(f"[{tipo}] Post publicado: {result.get('tema','?')}")
        else:
            logger.warning(f"[{tipo}] Falha ao publicar: {result}")

    async def start(self):
        li_config = LinkedInConfig()
        self.linkedin = LinkedInIntegration(config=li_config)
        await self.linkedin.initialize()
        self.running = True

        logger.info("=" * 55)
        logger.info("  AGENTE LINKEDIN - 3 POSTS/DIA (Render)")
        logger.info("  08:00 - Calendario (NR-1/LGPD/CBS/ESG/M1)")
        logger.info("  12:00 - News (educacional sobre agentes)")
        logger.info("  17:00 - Dica (dicas e insights)")
        logger.info("=" * 55)

        while self.running:
            try:
                if self.erros >= 5:
                    logger.warning("Muitos erros. Pausando 6h...")
                    await asyncio.sleep(21600)
                    self.erros = 0

                now = datetime.now()
                pendentes = self.tipos_pendentes()

                if pendentes:
                    for tipo in pendentes:
                        hora = now.hour
                        if (tipo == "calendario" and hora >= 8) or \
                           (tipo == "news" and hora >= 12) or \
                           (tipo == "dica" and hora >= 17):
                            logger.info(f"Publicando [{tipo}] as {now.strftime('%H:%M')}")
                            await self.postar(tipo)
                            await asyncio.sleep(60)
                else:
                    logger.info(f"3/3 posts hoje. Proximo ciclo em 30min.")

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

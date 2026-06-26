import asyncio
import json
import logging
import os
import sys

from aiokafka import AIOKafkaConsumer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.postgres_client import init_pool, close_pool, get_conn
from src.core.agent_loader import load_agent
from src.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aec_worker")

TOPIC = "aec.tasks"
GROUP_ID = "aec-worker-group"


async def process_task(task: dict) -> None:
    task_id = task["task_id"]
    agent_id = task["agent_id"]
    tenant_id = task["tenant_id"]

    async with get_conn() as conn:
        await conn.execute(
            "UPDATE agent_executions SET status='running', started_at=now() WHERE id=$1",
            task_id,
        )

    try:
        agent = load_agent(agent_id)
        settings = get_settings()
        result = await agent.execute(task["payload"], settings)

        async with get_conn() as conn:
            await conn.execute(
                """
                UPDATE agent_executions
                SET status='completed', completed_at=now(),
                    result_summary=$2, llm_tokens_used=$3
                WHERE id=$1
                """,
                task_id,
                str(result)[:1000],
                result.get("tokens_used", 0) if isinstance(result, dict) else 0,
            )
        logger.info("Task concluida: task=%s agent=%s", task_id, agent_id)

    except Exception:
        logger.exception("Erro ao processar task=%s agent=%s", task_id, agent_id)
        async with get_conn() as conn:
            await conn.execute(
                """
                UPDATE agent_executions
                SET status='failed', completed_at=now(), error_message=$2
                WHERE id=$1
                """,
                task_id,
                "Erro interno no worker — ver logs",
            )


async def run_worker() -> None:
    await init_pool()
    kafka_url = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=kafka_url,
        group_id=GROUP_ID,
        value_deserializer=lambda v: json.loads(v.decode()),
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )
    await consumer.start()
    logger.info("AEC Worker iniciado — consumindo topico: %s", TOPIC)

    try:
        async for msg in consumer:
            task = msg.value
            logger.info("Task recebida: task=%s agent=%s", task.get("task_id"), task.get("agent_id"))
            await process_task(task)
            await consumer.commit()
    finally:
        await consumer.stop()
        await close_pool()


if __name__ == "__main__":
    asyncio.run(run_worker())

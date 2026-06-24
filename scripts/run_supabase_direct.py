import asyncio
import asyncpg
from pathlib import Path

async def main():
    sql_path = Path(__file__).parent / "init-db.sql"
    sql = sql_path.read_text(encoding="utf-8")

    print("Conectando ao PostgreSQL via SSL...")
    try:
        conn = await asyncpg.connect(
            host="db.gveuivwuilhhwhzjdnvg.supabase.co",
            port=5432,
            user="postgres",
            password="sb_secret_anWk8djfzRHQoxUNnlRhiw_kWjcUE_O",
            database="postgres",
            ssl="require",
        )
        print("Conectado! Executando SQL...")
        await conn.execute(sql)
        print("SQL executado com sucesso! Tabelas criadas.")

        tables = await conn.fetch(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
        )
        print("Tabelas no schema public:", [t["table_name"] for t in tables])

        await conn.close()
    except Exception as e:
        print(f"Erro: {e}")

asyncio.run(main())

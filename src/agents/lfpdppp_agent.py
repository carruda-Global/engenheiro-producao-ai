import asyncio
from fastapi import APIRouter
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings

router = APIRouter(prefix="/api/lfpdppp", tags=["lfpdppp"])

SYSTEM_PROMPT = """Eres especialista en LFPDPPP (Ley Federal de Protección
de Datos Personales en Posesión de los Particulares) de México.
Genera un Aviso de Privacidad conforme a la ley, identifica
riesgos de tratamiento de datos personales, y recomienda acciones.
Multas: hasta 320,000 UMA."""


@router.post("/diagnostico")
async def diagnostico(data: dict):
    settings = Settings()
    deepseek = DeepSeekClient(settings)
    empresa = data.get("empresa", "")
    sector = data.get("sector", "")
    tipos_datos = data.get("tipos_datos", "")
    user_prompt = (
        f"Empresa: {empresa}\n"
        f"Sector: {sector}\n"
        f"Datos que maneja: {tipos_datos}"
    )
    response = await asyncio.to_thread(deepseek.chat, SYSTEM_PROMPT, user_prompt)
    return {
        "analysis": response,
        "checkout_url": "https://buy.stripe.com/4gw6oV9Jk8QRfC47u8g7e09",
    }

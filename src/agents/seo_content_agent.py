import asyncio
import itertools
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from openai import OpenAI
from src.database.supabase_client import SupabaseClient
from src.config import Settings

router = APIRouter(prefix="/api/seo", tags=["seo_agent"])

NORMAS_BR = {
    "nr1-psicossocial": {
        "nome": "NR-1 Psicossocial", "norma": "Portaria MTE 1.419/2024",
        "dor": "risco de interdição",
        "stripe_link": "https://buy.stripe.com/9B600l1Ac507blO29Og7e03",
    },
    "lgpd-operacional": {
        "nome": "LGPD Operacional", "norma": "Lei 13.709/2018",
        "dor": "multa até R$ 50M",
        "stripe_link": "https://buy.stripe.com/9B600l1Ac507blO29Og7e03",
    },
}

NORMAS_US = {
    "eu-ai-act-article-50": {
        "nome": "EU AI Act Article 50 Readiness", "norma": "EU AI Act Article 50",
        "dor": "fine up to EUR 35M or 7% global revenue",
        "stripe_link": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08",
    },
}
SETORES_US = ["saas", "fintech", "healthtech", "ecommerce", "martech"]

NORMAS_MX = {
    "lfpdppp-cumplimiento": {
        "nome": "Cumplimiento LFPDPPP", "norma": "LFPDPPP",
        "dor": "multas hasta 320,000 UMA",
        "stripe_link": "https://buy.stripe.com/4gw6oV9Jk8QRfC47u8g7e09",
    },
}
SETORES_MX = ["fintech", "ecommerce", "salud", "retail", "manufactura"]

NORMAS_CO = {
    "ley-1581-cumplimiento": {
        "nome": "Cumplimiento Ley 1581", "norma": "Ley 1581 de 2012",
        "dor": "multas hasta 2,000 SMMLV",
        "stripe_link": "https://buy.stripe.com/5kA00l5Ik6QRfC47u8g7e10",
    },
}
SETORES_CO = ["fintech", "salud", "retail", "logistica"]

NORMAS_AR = {
    "sdr-automatizacion": {
        "nome": "Automatización SDR y Back-Office", "norma": "Eficiencia operativa",
        "dor": "costo operativo elevado por procesos manuales",
        "stripe_link": "https://buy.stripe.com/9B600l1Ae6QRfC47u8g7e11",
    },
}
SETORES_AR = ["fintech", "agtech", "ecommerce", "servicios"]

PORTES = {
    "mei": "MEI/microempresas",
    "pequena-empresa": "pequeñas empresas",
    "media-empresa": "medianas empresas",
    "grande-empresa": "grandes empresas",
}

PORTES_EN = {
    "micro": "micro-business",
    "small": "small business",
    "medium": "medium company",
    "enterprise": "enterprise",
}

MARKET_CONFIGS = {
    "BR": (NORMAS_BR, ["industria", "comercio", "construcao-civil", "tecnologia", "saude"], PORTES, "português"),
    "US": (NORMAS_US, SETORES_US, PORTES_EN, "English"),
    "MX": (NORMAS_MX, SETORES_MX, PORTES, "español"),
    "CO": (NORMAS_CO, SETORES_CO, PORTES, "español"),
    "AR": (NORMAS_AR, SETORES_AR, PORTES, "español"),
}


class SEOContentAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    def _generate(self, prompt: str) -> str:
        resp = self.llm.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
        )
        return resp.choices[0].message.content or ""

    async def generate_market_pages(self, market: str):
        config = MARKET_CONFIGS.get(market)
        if not config:
            return {"error": f"Unknown market: {market}"}
        normas, setores, portes, _ = config
        combinations = list(itertools.product(normas.keys(), setores, portes.keys()))
        db = SupabaseClient(self.settings)
        generated = []
        for norma_key, setor, porte_key in combinations:
            slug = f"{market.lower()}-{norma_key}-{setor}-{porte_key}"
            norma = normas[norma_key]
            porte_label = portes[porte_key]
            idioma = config[3]
            prompt = (
                f"Write a landing page in {idioma} for:\n"
                f"Regulation: {norma['nome']} ({norma['norma']})\n"
                f"Sector: {setor}, Company size: {porte_label}\n"
                f"Pain: {norma['dor']}\n"
                f"Structure: H1, risk paragraph, 3 action bullets, "
                f"how agent solves in 48h, CTA.\n"
                f"Direct tone, real numbers, max 600 words."
            )
            try:
                content = await asyncio.to_thread(self._generate, prompt)
                page_data = {
                    "slug": slug,
                    "title": f"{norma['nome']} — {setor.title()} — {porte_label}",
                    "meta_description": f"{norma['nome']} ({norma['norma']}). {norma['dor']}.",
                    "body": content,
                    "stripe_link": norma["stripe_link"],
                    "market": market,
                    "published": True,
                }
                db.client.table("seo_pages").upsert(page_data).execute()
                generated.append(slug)
            except Exception as e:
                print(f"Erro ao gerar {slug}: {e}")
        return {"market": market, "pages_generated": len(generated)}


@router.post("/generate/{market}")
async def trigger_generation(market: str):
    agent = SEOContentAgent(Settings())
    return await agent.generate_market_pages(market.upper())


@router.get("/page/{slug}")
async def get_seo_page(slug: str):
    settings = Settings()
    db = SupabaseClient(settings)
    result = db.client.table("seo_pages").select("*").eq("slug", slug).execute()
    if not result.data:
        return {"error": "not_found"}
    page = result.data[0]
    title = page.get("title", slug)
    meta_desc = page.get("meta_description", "")
    body = page.get("body", "")
    link = page.get("stripe_link", "")
    html = (
        '<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        '<title>' + title + ' | SallesJam</title>'
        '<meta name="description" content="' + meta_desc + '">'
        '<meta name="robots" content="index,follow">'
        '<link rel="canonical" href="https://engenheiro-producao-ai.onrender.com/api/seo/page/' + slug + '">'
        '<style>body{font-family:sans-serif;background:#0C1322;color:#e2e8f0;padding:40px 24px}'
        'h1{color:#00C36B}.cta{display:inline-block;background:#00C36B;color:#fff;padding:14px 28px;border-radius:8px;text-decoration:none;font-weight:700;margin-top:20px}</style>'
        '</head><body><h1>' + title + '</h1><div>' + body + '</div>'
        '<a href="' + link + '" class="cta">Ativar SallesJam agora</a>'
        '</body></html>'
    )
    return HTMLResponse(content=html)

@router.get("/sitemap.xml")
async def sitemap():
    settings = Settings()
    db = SupabaseClient(settings)
    result = db.client.table("seo_pages").select("slug, market").eq("published", True).execute()
    items = []
    for p in result.data or []:
        slug = p["slug"]
        items.append('  <url><loc>https://engenheiro-producao-ai.onrender.com/api/seo/page/' + slug + '</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>')
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(items) + "\n</urlset>"
    return HTMLResponse(content=xml, media_type="application/xml")

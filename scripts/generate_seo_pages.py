"""Gera paginas SEO para todos os mercados e salva no Supabase."""
import itertools, time, sys
from openai import OpenAI
from src.config import Settings
from src.database.supabase_client import SupabaseClient

s = Settings()
llm = OpenAI(api_key=s.openrouter_api_key, base_url="https://openrouter.ai/api/v1")
db = SupabaseClient(s)

MARKETS = {
    "BR": {
        "normas": {
            "nr1-psicossocial": {"nome": "NR-1 Psicossocial", "norma": "Portaria MTE 1.419/2024", "dor": "risco de interdição", "link": "https://buy.stripe.com/9B600l1Ac507blO29Og7e03"},
            "lgpd-operacional": {"nome": "LGPD Operacional", "norma": "Lei 13.709/2018", "dor": "multa até R$ 50M", "link": "https://buy.stripe.com/9B600l1Ac507blO29Og7e03"},
        },
        "setores": ["industria", "comercio", "construcao-civil", "tecnologia", "saude"],
        "portes": {"micro": "microempresa", "pequena": "pequena empresa", "media": "media empresa", "grande": "grande empresa"},
        "idioma": "portugues",
    },
    "US": {
        "normas": {
            "eu-ai-act": {"nome": "EU AI Act Article 50 Readiness", "norma": "EU AI Act Article 50", "dor": "fine up to EUR 35M", "link": "https://buy.stripe.com/3cs00l1Ae6QRfC47u8g7e08"},
        },
        "setores": ["saas", "fintech", "healthtech", "ecommerce"],
        "portes": {"small": "small business", "medium": "medium company", "enterprise": "enterprise"},
        "idioma": "English",
    },
    "MX": {
        "normas": {
            "lfpdppp": {"nome": "Cumplimiento LFPDPPP", "norma": "LFPDPPP", "dor": "multas hasta 320,000 UMA", "link": "https://buy.stripe.com/4gw6oV9Jk8QRfC47u8g7e09"},
        },
        "setores": ["fintech", "ecommerce", "salud", "retail"],
        "portes": {"pequena": "pequena empresa", "media": "mediana empresa", "grande": "gran empresa"},
        "idioma": "espanol",
    },
    "CO": {
        "normas": {
            "ley1581": {"nome": "Cumplimiento Ley 1581", "norma": "Ley 1581 de 2012", "dor": "multas hasta 2,000 SMMLV", "link": "https://buy.stripe.com/5kA00l5Ik6QRfC47u8g7e10"},
        },
        "setores": ["fintech", "salud", "retail", "logistica"],
        "portes": {"pequena": "pequena empresa", "media": "mediana empresa", "grande": "gran empresa"},
        "idioma": "espanol",
    },
    "AR": {
        "normas": {
            "sdr-automation": {"nome": "Automatizacion SDR y Back-Office", "norma": "Eficiencia operativa", "dor": "costo operativo elevado", "link": "https://buy.stripe.com/9B600l1Ae6QRfC47u8g7e11"},
        },
        "setores": ["fintech", "ecommerce", "servicios"],
        "portes": {"pequena": "pequena empresa", "media": "mediana empresa", "grande": "gran empresa"},
        "idioma": "espanol",
    },
}

def generate_page(norma, setor, porte_label, idioma):
    prompt = (
        f"Write a landing page in {idioma} for:\n"
        f"Regulation: {norma['nome']} ({norma['norma']})\n"
        f"Sector: {setor}, Company size: {porte_label}\n"
        f"Pain: {norma['dor']}\n"
        f"Structure: H1, risk paragraph, 3 action bullets, "
        f"how agent solves in 48h, CTA with buy link.\n"
        f"Direct tone, real numbers, max 400 words."
    )
    resp = llm.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        timeout=30,
    )
    return resp.choices[0].message.content or ""

total = 0
for market_key, market in MARKETS.items():
    for nk, norma in market["normas"].items():
        for setor in market["setores"]:
            for pk, pl in market["portes"].items():
                slug = f"{market_key.lower()}-{nk}-{setor}-{pk}"
                title = f"{norma['nome']} - {setor.title()} - {pl}"
                meta = f"{norma['nome']} ({norma['norma']}). {norma['dor']}."
                try:
                    print(f"Gerando {slug}...", end=" ")
                    body = generate_page(norma, setor, pl, market["idioma"])
                    db.client.table("seo_pages").upsert({
                        "slug": slug, "title": title,
                        "meta_description": meta, "body": body,
                        "stripe_link": norma["link"],
                        "market": market_key, "published": True,
                    }).execute()
                    total += 1
                    print(f"OK ({total})")
                except Exception as e:
                    print(f"ERRO: {e}")
                time.sleep(1)

print(f"\nTotal gerado: {total} paginas")

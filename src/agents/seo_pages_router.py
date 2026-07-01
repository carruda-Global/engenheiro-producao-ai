from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/api/seo", tags=["seo_pages"])


@router.get("/page/{slug}")
async def get_seo_page(slug: str):
    import os, httpx
    supa_url = os.getenv("SUPABASE_URL", "")
    supa_key = os.getenv("SUPABASE_API_KEY", "")
    if not supa_url or not supa_key:
        return HTMLResponse(content="<h1>Servico indisponivel</h1>", status_code=503)
    try:
        headers = {"apikey": supa_key, "Authorization": "Bearer " + supa_key}
        r = httpx.get(supa_url + "/rest/v1/seo_pages?slug=eq." + slug + "&select=*", headers=headers, timeout=10)
        if r.status_code != 200 or not r.json():
            return HTMLResponse(content="<h1>Pagina nao encontrada</h1>", status_code=404)
        page = r.json()[0]
    except Exception as e:
        return HTMLResponse(content="<h1>Erro ao carregar pagina</h1>", status_code=500)
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
        '<style>body{font-family:sans-serif;background:#0C1322;color:#e2e8f0;padding:40px 24px}'
        'h1{color:#00C36B}.cta{display:inline-block;background:#00C36B;color:#fff;padding:14px 28px;border-radius:8px;text-decoration:none;font-weight:700;margin-top:20px}</style>'
        '</head><body><h1>' + title + '</h1><div>' + body + '</div>'
        '<a href="' + link + '" class="cta">Ativar SallesJam agora</a>'
        '</body></html>'
    )
    return HTMLResponse(content=html)


@router.get("/sitemap.xml")
async def sitemap():
    import os, httpx
    supa_url = os.getenv("SUPABASE_URL", "")
    supa_key = os.getenv("SUPABASE_API_KEY", "")
    if not supa_url or not supa_key:
        return HTMLResponse(content="", status_code=503)
    try:
        headers = {"apikey": supa_key, "Authorization": "Bearer " + supa_key}
        r = httpx.get(supa_url + "/rest/v1/seo_pages?select=slug,market&published=eq.true", headers=headers, timeout=10)
        pages = r.json()
    except:
        return HTMLResponse(content="", status_code=500)
    items = []
    for p in pages or []:
        items.append('  <url><loc>https://global-engenharia.com/artigos/' + p["slug"] + '</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>')
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(items) + "\n</urlset>"
    return HTMLResponse(content=xml, media_type="application/xml")

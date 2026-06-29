import os, json
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI

router = APIRouter(prefix="/diagnostico", tags=["diagnosticos"])

API_KEY = os.getenv("OPENROUTER_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")

AGENTES = {
    "nr1": {
        "nome": "NR-1 Psicossocial",
        "icone": "🧠",
        "lei": "Portaria MTE 1.419/2024",
        "descricao": "Inventario de Riscos Psicossociais (FRPRT)",
        "system_prompt": (
            "Voce e um especialista em riscos psicossociais no trabalho conforme "
            "a NR-1 (Portaria MTE 1.419/2024). Sua funcao e identificar, avaliar "
            "e documentar Fatores de Riscos Psicossociais Relacionados ao Trabalho "
            "(FRPRT) usando metodologias validadas como COPSOQ, JCQ, PHQ-9 e GAD-7. "
            "Gere inventarios, planos de acao e relatorios executivos. "
            "Ao final inclua o rodape legal padrao."
        ),
        "campos": [
            {"nome": "Nome da empresa", "id": "nome", "placeholder": "Ex: Metalurgica ABC Ltda"},
            {"nome": "Setor", "id": "setor", "placeholder": "Ex: Metalurgia, Saude"},
            {"nome": "Funcionarios", "id": "func", "placeholder": "Ex: 150"},
            {"nome": "Jornada", "id": "jornada", "placeholder": "Ex: 44h, turnos alternantes"},
            {"nome": "Observacoes", "id": "obs", "placeholder": "Absenteismo, turnover, queixas...", "textarea": True},
        ],
        "prompt_template": (
            "Dados da empresa:\nNome: {nome}\nSetor: {setor}\nFuncionarios: {func}\n"
            "Jornada: {jornada}\nObservacoes: {obs}\n\n"
            "Realize a identificacao e classificacao dos FRPRT conforme NR-1. "
            "Para cada fator: descricao, classificacao, grupo FRPRT e metodo de avaliacao. "
            "Gere inventario completo. Inclua o rodape legal ao final."
        ),
        "rodape": (
            "\n\n---\n\n"
            "**Documento gerado pelo AION 7.0 — Agente NR-1 Psicossocial**\n\n"
            "Base legal: Portaria MTE n\u00ba 1.419/2024, Manual GRO/NR-1 MTE 2026.\n"
            "Metodologias: COPSOQ III, JCQ, PHQ-9, GAD-7.\n"
            "Responsavel tecnico: Profissional com conhecimento tecnico compativel.\n"
            "Este documento NAO substitui o PGR completo nem dispensa ART para riscos fisicos, quimicos, biologicos e ergonomicos.\n\n"
            "Emitido por Global Match Engenharia de Producao"
        ),
    },
}


HTML_BASE = """<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<title>AION 7.0 - {nome}</title>
<script src="https://cdn.jsdelivr.net/npm/markdown-it@14/dist/markdown-it.min.js"></script>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f1f5f9;color:#1e293b;padding:20px}}
.container{{max-width:800px;margin:0 auto}}
h1{{font-size:24px;color:#0f172a}}.sub{{color:#64748b;font-size:14px;margin-bottom:24px}}
.card{{background:#fff;border-radius:12px;padding:24px;margin-bottom:16px;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
label{{display:block;font-weight:600;font-size:14px;margin-bottom:4px;color:#334155}}
input,textarea{{width:100%;padding:10px 12px;border:1px solid #cbd5e1;border-radius:8px;font-size:14px;margin-bottom:16px;font-family:inherit}}
textarea{{height:80px;resize:vertical}}
button{{background:#2563eb;color:#fff;border:none;padding:12px 24px;border-radius:8px;font-size:15px;font-weight:600;cursor:pointer}}
button:hover{{background:#1d4ed8}}
.loading{{display:none;text-align:center;padding:40px;color:#2563eb;font-weight:600}}
.resultado{{display:none}}
.resultado h2{{font-size:18px;margin:12px 0;padding-bottom:8px;border-bottom:2px solid #e2e8f0}}
#output{{font-family:inherit;font-size:14px;line-height:1.6;background:#f8fafc;padding:16px;border-radius:8px;border:1px solid #e2e8f0;max-height:800px;overflow-y:auto}}
#output table{{border-collapse:collapse;width:100%;margin:8px 0;font-size:13px}}
#output td,#output th{{border:1px solid #e2e8f0;padding:8px 10px;text-align:left;vertical-align:top}}
#output th{{background:#f1f5f9;font-weight:600}}
#output h3{{margin:16px 0 8px;color:#0f172a}}
.erro{{color:#dc2626;font-weight:600}}
.spinner{{display:inline-block;width:24px;height:24px;border:3px solid #e2e8f0;border-top:3px solid #2563eb;border-radius:50%;animation:spin .8s linear infinite;margin-right:8px;vertical-align:middle}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@media print{{body{{background:#fff;padding:10px}}.card{{box-shadow:none;border:1px solid #e2e8f0}}.no-print{{display:none!important}}}}
</style></head>
<body>
<div class="container">
<h1>{icone} {nome}</h1>
<p class="sub">{lei} — {descricao}</p>
<div class="card" id="formCard">
<form id="form">
{campos}
<button type="submit" class="no-print">Gerar Documento</button>
</form></div>
<div class="loading" id="loading"><div class="spinner"></div> Processando com IA... aguarde</div>
<div class="card resultado" id="resultArea">
<div class="no-print" style="text-align:right;margin-bottom:12px">
<button onclick="window.print()">Imprimir / PDF</button>
<button onclick="location.reload()" style="background:#64748b;margin-left:8px">Novo</button>
</div>
<h2>{nome} — Documento Gerado</h2>
<p style="color:#64748b;font-size:13px;margin-bottom:12px" id="empresaInfo"></p>
<div id="output"></div>
</div></div>
<script>
document.getElementById('form').onsubmit = async function(e) {{
e.preventDefault();
var f = new FormData(this), d = Object.fromEntries(f);
document.getElementById('empresaInfo').textContent = 'Empresa: ' + (d.nome || 'N/I');
document.getElementById('formCard').style.display = 'none';
document.getElementById('loading').style.display = 'block';
try {{
var r = await fetch('/diagnostico/{agente_id}/gerar', {{
method:'POST',
headers:{{'Content-Type':'application/json'}},
body: JSON.stringify(d)
}});
var j = await r.json();
document.getElementById('loading').style.display = 'none';
document.getElementById('resultArea').style.display = 'block';
if (j.erro) {{
document.getElementById('output').innerHTML = '<p class="erro">' + j.erro + '</p>';
}} else {{
var md = window.markdownit();
document.getElementById('output').innerHTML = md.render(j.conteudo);
}}
}} catch(err) {{
document.getElementById('loading').style.display = 'none';
document.getElementById('resultArea').style.display = 'block';
document.getElementById('output').innerHTML = '<p class="erro">Erro: ' + err.message + '</p>';
}}
}};
</script></body></html>"""


def montar_campos(campos: list) -> str:
    html = ""
    for c in campos:
        if c.get("textarea"):
            html += f'<label>{c["nome"]}</label>\n<textarea id="{c["id"]}" name="{c["id"]}" placeholder="{c["placeholder"]}"></textarea>\n'
        else:
            html += f'<label>{c["nome"]}</label>\n<input id="{c["id"]}" name="{c["id"]}" placeholder="{c["placeholder"]}">\n'
    return html


@router.get("/{agente_id}", response_class=HTMLResponse)
async def page(agente_id: str):
    info = AGENTES.get(agente_id)
    if not info:
        return HTMLResponse("<h1>Agente nao encontrado</h1>", status_code=404)
    html = HTML_BASE.format(
        nome=info["nome"],
        icone=info["icone"],
        lei=info["lei"],
        descricao=info["descricao"],
        agente_id=agente_id,
        campos=montar_campos(info["campos"]),
    )
    return HTMLResponse(html)


@router.post("/{agente_id}/gerar")
async def gerar(agente_id: str, dados: dict):
    info = AGENTES.get(agente_id)
    if not info:
        return JSONResponse({"erro": "Agente nao encontrado"}, status_code=404)

    prompt = info["prompt_template"].format(
        nome=dados.get("nome", "N/I"),
        setor=dados.get("setor", "N/I"),
        func=dados.get("func", "N/I"),
        jornada=dados.get("jornada", "N/I"),
        obs=dados.get("obs", "N/I"),
    )

    try:
        client = OpenAI(api_key=API_KEY, base_url="https://openrouter.ai/api/v1", timeout=60)
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": info["system_prompt"]},
                {"role": "user", "content": prompt},
            ],
            max_tokens=4096,
        )
        conteudo = resp.choices[0].message.content + info["rodape"]
        return JSONResponse({"conteudo": conteudo})
    except Exception as e:
        return JSONResponse({"erro": str(e)})

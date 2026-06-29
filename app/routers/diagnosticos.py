import os, json, time, hashlib, hmac
from collections import defaultdict
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI

router = APIRouter(prefix="/aion", tags=["aion"])

API_KEY = os.getenv("OPENROUTER_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")
SECRET = os.getenv("AION_SECRET", "aion-secret-2026")

RATE_LIMIT = defaultdict(list)
TOKENS = {}

AGENTES = {
    "nr1": {
        "nome": "NR-1 Psicossocial", "icone": "🧠",
        "lei": "Portaria MTE 1.419/2024",
        "descricao": "Inventario de Riscos Psicossociais (FRPRT)",
        "system_prompt": "Voce e um especialista em riscos psicossociais no trabalho conforme a NR-1 (Portaria MTE 1.419/2024). Identifique, avalie e documente FRPRT usando COPSOQ, JCQ, PHQ-9 e GAD-7. Gere inventario completo.",
        "campos": [
            {"nome": "Nome da empresa", "id": "nome", "placeholder": "Ex: Metalurgica ABC Ltda"},
            {"nome": "Setor", "id": "setor", "placeholder": "Ex: Metalurgia, Saude"},
            {"nome": "Funcionarios", "id": "func", "placeholder": "Ex: 150"},
            {"nome": "Jornada", "id": "jornada", "placeholder": "Ex: 44h, turnos alternantes"},
            {"nome": "Observacoes", "id": "obs", "placeholder": "Absenteismo, turnover, queixas...", "textarea": True},
        ],
        "prompt_template": "Dados da empresa:\nNome: {nome}\nCNPJ: {cnpj}\nEndereco: {endereco}\nSetor: {setor}\nFuncionarios: {func}\nJornada: {jornada}\nObs: {obs}\n\nIdentifique e classifique os FRPRT conforme NR-1. Para cada fator: descricao, classificacao, grupo FRPRT e metodo. Gere inventario completo.",
        "rodape": "\n\n---\n\n**Documento gerado pelo AION 7.0 — Agente NR-1 Psicossocial**\n\nBase legal: Portaria MTE 1.419/2024, Manual GRO/NR-1 MTE 2026.\nMetodologias: COPSOQ III, JCQ, PHQ-9, GAD-7.\nResponsavel tecnico: Profissional com conhecimento tecnico compativel.\nEste documento NAO substitui o PGR completo nem dispensa ART.\n\nEmitido por Global Match Engenharia de Producao",
    },
    "lgpd": {
        "nome": "LGPD Operacional", "icone": "🔒",
        "lei": "Lei 13.709/2018",
        "descricao": "Mapeamento de Dados e RoPA",
        "system_prompt": "Voce e um especialista em LGPD (Lei 13.709/2018). Sua funcao e mapear dados pessoais, gerar RoPA e identificar conformidade com ANPD.",
        "campos": [
            {"nome": "Nome da empresa", "id": "nome", "placeholder": "Ex: Escritorio ABC Ltda"},
            {"nome": "Setor", "id": "setor", "placeholder": "Ex: Saude, Financeiro"},
            {"nome": "Funcionarios", "id": "func", "placeholder": "Ex: 50"},
            {"nome": "Tipo de dados tratados", "id": "obs", "placeholder": "Ex: Dados de clientes, funcionarios, fornecedores", "textarea": True},
        ],
        "prompt_template": "Dados:\nEmpresa: {nome}\nCNPJ: {cnpj}\nEndereco: {endereco}\nSetor: {setor}\nFuncionarios: {func}\nDados tratados: {obs}\n\nGere um RoPA (Registro de Atividades de Tratamento) completo conforme LGPD. Inclua: base legal, categoria de dados, finalidade, compartilhamento e prazo de retencao.",
        "rodape": "\n\n---\n\n**Documento gerado pelo AION 7.0 — Agente LGPD Operacional**\n\nBase legal: Lei 13.709/2018.\n\nEmitido por Global Match Engenharia de Producao",
    },
    "cbs_ibs": {
        "nome": "CBS/IBS Tributario", "icone": "💰",
        "lei": "LC 214/2025",
        "descricao": "Classificacao NCM e simulacao fiscal",
        "system_prompt": "Voce e um especialista em reforma tributaria brasileira LC 214/2025. Sua funcao e classificar NCM, simular impacto de CBS/IBS e gerar DeRE.",
        "campos": [
            {"nome": "Nome da empresa", "id": "nome", "placeholder": "Ex: Comercio ABC Ltda"},
            {"nome": "Setor", "id": "setor", "placeholder": "Ex: Industria, Comercio, Servicos"},
            {"nome": "Faturamento mensal estimado", "id": "func", "placeholder": "Ex: R$ 200.000"},
            {"nome": "Produtos/servicos comercializados", "id": "obs", "placeholder": "Ex: Venda de equipamentos, prestacao de servicos de instalacao", "textarea": True},
        ],
        "prompt_template": "Dados:\nEmpresa: {nome}\nCNPJ: {cnpj}\nEndereco: {endereco}\nSetor: {setor}\nFaturamento: {func}\nProdutos: {obs}\n\nGere um relatorio de classificacao NCM e simulacao de impacto CBS/IBS conforme LC 214/2025. Inclua aliquotas, cenarios e recomendacoes.",
        "rodape": "\n\n---\n\n**Documento gerado pelo AION 7.0 — Agente CBS/IBS Tributario**\n\nBase legal: LC 214/2025.\n\nEmitido por Global Match Engenharia de Producao",
    },
    "esg": {
        "nome": "ESG IFRS S1/S2", "icone": "🌿",
        "lei": "Res. CVM 193/2023",
        "descricao": "Diagnostico ESG e relatorios IFRS",
        "system_prompt": "Voce e um especialista em ESG e IFRS S1/S2. Sua funcao e gerar diagnosticos ESG, relatorios IFRS e identificar impactos de sustentabilidade.",
        "campos": [
            {"nome": "Nome da empresa", "id": "nome", "placeholder": "Ex: Industria ABC"},
            {"nome": "Setor", "id": "setor", "placeholder": "Ex: Industria, Varejo"},
            {"nome": "Funcionarios", "id": "func", "placeholder": "Ex: 200"},
            {"nome": "Informacoes adicionais", "id": "obs", "placeholder": "Ex: Possui certificacao ISO, exporta para Europa, consome muita energia", "textarea": True},
        ],
        "prompt_template": "Dados:\nEmpresa: {nome}\nCNPJ: {cnpj}\nEndereco: {endereco}\nSetor: {setor}\nFuncionarios: {func}\nInfo: {obs}\n\nGere um diagnostico ESG preliminar conforme IFRS S1/S2. Inclua: riscos e oportunidades ESG, metricas atuais e recomendacoes.",
        "rodape": "\n\n---\n\n**Documento gerado pelo AION 7.0 — Agente ESG IFRS S1/S2**\n\nBase legal: Res. CVM 193/2023, IFRS S1/S2.\n\nEmitido por Global Match Engenharia de Producao",
    },
    "denuncias": {
        "nome": "Canal de Denuncias", "icone": "📢",
        "lei": "Lei 14.457/2022",
        "descricao": "Implementacao de canal de denuncias",
        "system_prompt": "Voce e um especialista em canal de denuncias conforme Lei 14.457/2022. Sua funcao e orientar sobre implementacao, fluxos de apuracao e conformidade.",
        "campos": [
            {"nome": "Nome da empresa", "id": "nome", "placeholder": "Ex: Empresa ABC"},
            {"nome": "Setor", "id": "setor", "placeholder": "Ex: Saude, Industria"},
            {"nome": "Funcionarios", "id": "func", "placeholder": "Ex: 120"},
            {"nome": "Canal atual (se houver)", "id": "obs", "placeholder": "Ex: Nao possui, apenas email informal", "textarea": True},
        ],
        "prompt_template": "Dados:\nEmpresa: {nome}\nCNPJ: {cnpj}\nEndereco: {endereco}\nSetor: {setor}\nFuncionarios: {func}\nCanal atual: {obs}\n\nGere um plano de implementacao de canal de denuncias conforme Lei 14.457/2022. Inclua: canais obrigatorios, fluxo de apuracao, prazos e modelo de relatorio.",
        "rodape": "\n\n---\n\n**Documento gerado pelo AION 7.0 — Agente Canal de Denuncias**\n\nBase legal: Lei 14.457/2022.\n\nEmitido por Global Match Engenharia de Producao",
    },
    "igualdade": {
        "nome": "Igualdade Salarial", "icone": "⚖️",
        "lei": "Lei 14.611/2023",
        "descricao": "Relatorio de equidade salarial",
        "system_prompt": "Voce e um especialista em igualdade salarial conforme Lei 14.611/2023. Sua funcao e analisar equidade, gerar relatorio MTE e plano de adequacao.",
        "campos": [
            {"nome": "Nome da empresa", "id": "nome", "placeholder": "Ex: Empresa ABC"},
            {"nome": "Setor", "id": "setor", "placeholder": "Ex: Comercio, Industria"},
            {"nome": "Total de funcionarios", "id": "func", "placeholder": "Ex: 80 homens, 60 mulheres"},
            {"nome": "Dados salariais (cargos e faixas)", "id": "obs", "placeholder": "Ex: 3 diretores (2H/1M), 20 gerentes (12H/8M), 60 operadores (40H/20M)", "textarea": True},
        ],
        "prompt_template": "Dados:\nEmpresa: {nome}\nCNPJ: {cnpj}\nEndereco: {endereco}\nSetor: {setor}\nQuadro: {func}\nSalarios: {obs}\n\nGere um relatorio de equidade salarial conforme Lei 14.611/2023. Inclua: analise por cargo, gap salarial por genero, plano de adequacao e cronograma.",
        "rodape": "\n\n---\n\n**Documento gerado pelo AION 7.0 — Agente Igualdade Salarial**\n\nBase legal: Lei 14.611/2023.\n\nEmitido por Global Match Engenharia de Producao",
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
@media print{{body{{background:#fff;padding:10px}}.card{{box-shadow:none;border:1px solid #e2e8f0}}.no-print{{display:none!important}}#output{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}}}
/* Anti-copy */body{{-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;user-select:none}}#output{{-webkit-user-select:text;-moz-user-select:text;-ms-user-select:text;user-select:text}}
</style>
<script>
document.oncontextmenu=function(e){{e.preventDefault();return false}};
document.onkeydown=function(e){{if(e.ctrlKey&&(e.key==='c'||e.key==='C'||e.key==='u'||e.key==='U'||e.key==='s'||e.key==='S')){{e.preventDefault();return false}};if(e.key==='F12'){{e.preventDefault();return false}}}};
</script>
</head>
<body>
<div class="container">
<h1>{icone} {nome}</h1>
<p class="sub">{lei} — {descricao}</p>
<div class="card" id="formCard">
<form id="form">
<div style="display:none"><input name="hp" tabindex="-1" autocomplete="off"></div>
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
var r = await fetch('/aion/{agente_id}/gerar', {{
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


def check_rate_limit(ip: str):
    now = time.time()
    RATE_LIMIT[ip] = [t for t in RATE_LIMIT[ip] if now - t < 60]
    if len(RATE_LIMIT[ip]) >= 5:
        raise HTTPException(status_code=429, detail="Muitas requisicoes. Aguarde 1 minuto.")
    RATE_LIMIT[ip].append(now)


def gerar_token(agente_id: str, empresa: str) -> str:
    payload = f"{agente_id}:{empresa}:{int(time.time())}:{SECRET}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def montar_campos(campos: list) -> str:
    html = ""
    for c in campos:
        if c["id"] == "nome":
            html += f'<label>{c["nome"]}</label>\n<input id="{c["id"]}" name="{c["id"]}" placeholder="{c["placeholder"]}">\n'
            html += '<label>CNPJ</label>\n<input id="cnpj" name="cnpj" placeholder="Ex: 00.000.000/0001-00">\n'
            html += '<label>Endereco</label>\n<input id="endereco" name="endereco" placeholder="Ex: Rua Exemplo, 123 - Sao Paulo - SP">\n'
        elif c.get("textarea"):
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
async def gerar(agente_id: str, dados: dict, request: Request):
    info = AGENTES.get(agente_id)
    if not info:
        return JSONResponse({"erro": "Agente nao encontrado"}, status_code=404)

    check_rate_limit(request.client.host if request.client else "unknown")

    if dados.get("hp", ""):
        return JSONResponse({"erro": "Acesso negado"})

    prompt = info["prompt_template"].format(
        nome=dados.get("nome", "N/I"),
        cnpj=dados.get("cnpj", "N/I"),
        endereco=dados.get("endereco", "N/I"),
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
        token = gerar_token(agente_id, dados.get("nome", "N/I"))
        rodape_com_token = info["rodape"] + f"\nProtocolo: {token}"
        conteudo = resp.choices[0].message.content + rodape_com_token
        return JSONResponse({"conteudo": conteudo, "token": token})
    except Exception as e:
        return JSONResponse({"erro": str(e)})

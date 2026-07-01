# Ações Manuais — Visibilidade Global (não automatizáveis por exigirem conta/login)

Tudo que podia ser automatizado por código já está rodando (llms.txt, diretórios regionais,
press release x402, MCP manifests). O que resta abaixo exige criar conta em serviço de
terceiro — não posso fazer isso por você, mas deixei tudo pronto para copiar e colar.

---

## 1. Registry MCP oficial (Anthropic) — ~5 min, 3 comandos

**Correção:** não é PR — é uma CLI (`mcp-publisher`) com login OAuth do GitHub (device
flow, você autoriza no navegador). Os 3 `server.json` já estão prontos em
[`mcp-registry/`](../mcp-registry/) (regulatory, esg, erp) — só rodar:

```powershell
# 1. Instalar (Windows PowerShell)
$arch = if ([System.Runtime.InteropServices.RuntimeInformation]::ProcessArchitecture -eq "Arm64") { "arm64" } else { "amd64" }
Invoke-WebRequest -Uri "https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_windows_$arch.tar.gz" -OutFile "mcp-publisher.tar.gz"
tar xf mcp-publisher.tar.gz mcp-publisher.exe

# 2. Login (abre o navegador, pede pra autorizar — só você pode fazer isso)
.\mcp-publisher.exe login github

# 3. Publicar os 3 servidores (rodar de dentro de AION 7.0/mcp-registry/)
cd mcp-registry
..\mcp-publisher.exe publish --file regulatory.server.json
..\mcp-publisher.exe publish --file esg.server.json
..\mcp-publisher.exe publish --file erp.server.json
```

> Nota: o campo `name` usa `io.github.carruda-global/...` — se seu login pessoal do GitHub
> for diferente de `carruda-global`, ajuste o campo `name` nos 3 arquivos antes de publicar
> (precisa bater com o namespace do usuário autenticado).

## 2. Outros registries MCP (Smithery, Glama, PulseMCP, mcp.so) — 10 min

Esses são formulários web (exigem conta própria). Usar a URL do manifest existente:
`https://engenheiro-producao-ai.onrender.com/mcp/{server_id}/manifest` (regulatory, esg, erp)

| Registry | Link de submissão |
|---|---|
| Smithery | smithery.ai/new |
| Glama | glama.ai/mcp/servers (botão "Submit") |
| PulseMCP | pulsemcp.com/submit |
| mcp.so | mcp.so/submit |

**Descrição padrão (copiar e colar):**
> EcoSystem AEC Regulatory/ESG/ERP MCP Servers — 3 Model Context Protocol servers exposing AI compliance tools (LGPD/GDPR, NR-1, ESG/carbon inventory, ERP integrations for Dynamics/Salesforce/Oracle/SAP). Built by Global Match Engenharia (Brazil). SSE transport, no auth required for read-only tool discovery.

---

## 3. Crunchbase — 5 min (crunchbase.com/add-new-organization)

```
Company name: Global Match Engenharia (EcoSystem AEC)
Website: https://global-engenharia.com/ecosystem
Short description: AI compliance automation platform with 106 specialized agents covering EU AI Act, LGPD/GDPR, CSRD, DORA, NIS2, SOC2, ISO27001 and NR-1. Sold as SaaS subscriptions and pay-per-use via x402/USDC to both human customers and autonomous AI agents.
Industry: Regulatory Technology (RegTech), Artificial Intelligence, Compliance Software
Founded: 2024
Headquarters: São Paulo, Brazil
Company type: Privately held, bootstrapped
```

## 4. Wellfound / AngelList — 5 min (wellfound.com/company/new)

```
Tagline: 106 AI agents for global compliance — EU AI Act, LGPD, CSRD, DORA, NR-1
Description: (same as Crunchbase above)
Markets: Brazil, USA, Mexico, Colombia, Argentina, India, UAE, European Union
```

---

## Já implementado automaticamente (não precisa fazer nada)

- `/llms.txt` servido pela API — descoberta por ChatGPT/Perplexity/Claude
- 5 diretórios regionais (Tracxn, Inc42, MAGNiTT, EU-Startups, LatamList) — entram na rotação
  de 72h existente (`auto_job_directories`), e-mail de rascunho chega para
  carruda2307@gmail.com encaminhar
- Press release do marco x402/A2A — alterna com o press release original a cada ciclo de
  14 dias (`auto_job_press_release_distribution`), publicado automaticamente no Dev.to,
  Reddit e nas 5 publicações RegTech

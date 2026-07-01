# Ações Manuais — Visibilidade Global (não automatizáveis por exigirem conta/login)

Tudo que podia ser automatizado por código já está rodando (llms.txt, diretórios regionais,
press release x402, MCP manifests). O que resta abaixo exige criar conta em serviço de
terceiro — não posso fazer isso por você, mas deixei tudo pronto para copiar e colar.

---

## 1. Registries MCP (Model Context Protocol) — 10-15 min

A AION já expõe o manifest de cada servidor MCP publicamente:
- `https://engenheiro-producao-ai.onrender.com/mcp/servers` (lista os 4 servidores)
- `https://engenheiro-producao-ai.onrender.com/mcp/{server_id}/manifest` (regulatory, esg, erp, microsoft)

Use essas URLs ao submeter em:

| Registry | Link de submissão | O que colar |
|---|---|---|
| MCP oficial (Anthropic) | github.com/modelcontextprotocol/registry → abrir PR | URL do manifest + descrição abaixo |
| Smithery | smithery.ai/new | URL do manifest + descrição abaixo |
| Glama | glama.ai/mcp/servers (botão "Submit") | URL do manifest + descrição abaixo |
| PulseMCP | pulsemcp.com/submit | URL do manifest + descrição abaixo |
| mcp.so | mcp.so/submit | URL do manifest + descrição abaixo |

**Descrição padrão (copiar e colar):**
> EcoSystem AEC Regulatory/ESG/ERP/Microsoft MCP Servers — 4 Model Context Protocol servers exposing AI compliance tools (EU AI Act, LGPD/GDPR, NR-1, ESG/carbon inventory, ERP integrations for Dynamics/Salesforce/Oracle/SAP). Built by Global Match Engenharia (Brazil). SSE transport, no auth required for read-only tool discovery.

---

## 2. Crunchbase — 5 min (crunchbase.com/add-new-organization)

```
Company name: Global Match Engenharia (EcoSystem AEC)
Website: https://global-engenharia.com/ecosystem
Short description: AI compliance automation platform with 106 specialized agents covering EU AI Act, LGPD/GDPR, CSRD, DORA, NIS2, SOC2, ISO27001 and NR-1. Sold as SaaS subscriptions and pay-per-use via x402/USDC to both human customers and autonomous AI agents.
Industry: Regulatory Technology (RegTech), Artificial Intelligence, Compliance Software
Founded: 2024
Headquarters: São Paulo, Brazil
Company type: Privately held, bootstrapped
```

## 3. Wellfound / AngelList — 5 min (wellfound.com/company/new)

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

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

## 4. Vídeo — roteiros prontos (60-90s cada, gravação por conta própria)

Formato sugerido: screen recording da tela de vendas + voz sobre resultado de um diagnóstico
real. Publicar como YouTube Shorts (atinge Índia/LATAM/MENA melhor que texto em inglês).

### Roteiro 1 — EU AI Act (mercado EUA/UE)
1. "Is your AI system high-risk under the EU AI Act? You have until August 2026 to find out."
2. [tela: formulário de nome da empresa + setor]
3. "In under a second, our AI agent classifies your system and gives you an action plan."
4. [tela: resultado com risk score e findings]
5. "EcoSystem AEC — global-engenharia.com/ecosystem"

### Roteiro 2 — NR-1 (mercado Brasil)
1. "Sua empresa já fez o inventário de riscos psicossociais da NR-1? O prazo já passou."
2. [tela: diagnóstico rodando]
3. "Nosso agente de IA gera o FRPRT e o plano de ação em segundos."
4. [tela: resultado]
5. "EcoSystem AEC — global-engenharia.com/ecosystem"

### Roteiro 3 — Agent-to-Agent (ângulo técnico/dev, para YouTube + Dev.to embed)
1. "We made our compliance AI payable by other AI agents. No login. No credit card."
2. [tela: curl mostrando HTTP 402 → pagamento USDC → resposta]
3. "x402 protocol, live on Base network, registered on 9 agent marketplaces."
4. "engenheiro-producao-ai.onrender.com/.well-known/agent-card.json"

---

## Já implementado automaticamente (não precisa fazer nada)

- `/llms.txt` servido pela API — descoberta por ChatGPT/Perplexity/Claude
- 5 diretórios regionais (Tracxn, Inc42, MAGNiTT, EU-Startups, LatamList) — entram na rotação
  de 72h existente (`auto_job_directories`), e-mail de rascunho chega para
  carruda2307@gmail.com encaminhar
- Press release do marco x402/A2A — alterna com o press release original a cada ciclo de
  14 dias (`auto_job_press_release_distribution`), publicado automaticamente no Dev.to,
  Reddit e nas 5 publicações RegTech

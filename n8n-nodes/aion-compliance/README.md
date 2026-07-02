# n8n-nodes-aion-compliance

n8n community node for AION Compliance. Execute checks de compliance regulatorio com 106 agentes de IA diretamente dos seus workflows n8n.

## Instalacao

### Via n8n (instancia propria)

```bash
npm install n8n-nodes-aion-compliance
```

### Via n8n.io (cloud/desktop)

Settings → Community Nodes → Install → `n8n-nodes-aion-compliance`

## Credentials

| Field | Description |
|-------|-------------|
| API Key | Sua chave de API do AION |
| Base URL | URL base da API (default: `https://engenheiro-producao-ai.onrender.com`) |

## Services Disponiveis

| Service | Descricao | Preco USDC |
|---------|-----------|-----------|
| NR-1 Psychosocial Risk | Diagnostico de riscos psicossociais | 0.50 USDC |
| LGPD Privacy Scan | Varredura de dados pessoais | 0.75 USDC |
| EU AI Act Readiness | Classificacao de sistemas de IA | 1.00 USDC |
| CSRD Double Materiality | Avaliacao de materialidade dupla | 1.50 USDC |
| Carbon Inventory Scope 1+2 | Inventario de carbono | 1.00 USDC |
| Vendor Risk Assessment | Avaliacao de risco de fornecedores | 0.50 USDC |
| Contract Risk Analysis | Analise de risco contratual | 0.50 USDC |
| M&A Due Diligence | Due diligence de compliance | 2.00 USDC |

## Publicacao no n8n Community Registry

1. Build: `npm run build && npm pack`
2. Publique no npm: `npm publish`
3. O n8n Community Registry indexa automaticamente

## Workflows Sugeridos

1. **Webhook → NR-1 Check → Email Report**
   - Recebe dados via webhook, executa NR-1 check, envia relatorio por email

2. **Schedule → EU AI Act Check → Slack Notification**
   - Verificacao semanal de conformidade EU AI Act com alerta no Slack

3. **HubSpot Trigger → LGPD Scan → Update CRM**
   - Quando contato e criado no HubSpot, executa LGPD scan e atualiza CRM

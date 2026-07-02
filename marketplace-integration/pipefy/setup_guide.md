# Pipefy Ecosystem — Setup Guide

## 1. Criar App no Pipefy

1. Acesse https://app.pipefy.com/developers
2. Clique em "Create App"
3. Preencha:
   - **Name:** AION Compliance
   - **Description:** 106 agentes de IA para compliance regulatorio dentro dos seus Pipes
   - **Categories:** "Compliance", "AI & Automation"
   - **Permissions:** `read:pipe`, `write:card`, `read:card`, `read:organization`

4. Copie a **API Key** gerada

## 2. Criar Pipes de Compliance

Crie 3 Pipes no Pipefy:

| Pipe | ID | Funcao |
|------|-----|--------|
| AION NR-1 Psicossocial | `PIPEFY_PIPE_COMPLIANCE_NR1` | Diagnostico de riscos psicossociais |
| AION LGPD Scanner | `PIPEFY_PIPE_COMPLIANCE_LGPD` | Varredura de dados pessoais |
| AION EU AI Act | `PIPEFY_PIPE_COMPLIANCE_EU_AI_ACT` | Classificacao de sistemas de IA |

Cada Pipe deve ter campos:
- `service` (text) — nome do servico
- `card_id` (text) — card de origem
- `status` (select) — pending / processing / completed / error
- `result` (text) — resultado JSON do check

## 3. Webhooks

Configure webhooks nos Pipes:

Pipefy Developer Portal → Seu App → Webhooks

**URL:** `https://engenheiro-producao-ai.onrender.com/pipefy/webhook`

**Eventos:** `card.create`, `card.delete`, `card.update`, `phase.change`

## 4. Configurar no Render

```bash
PIPEFY_API_KEY=sua-api-key
PIPEFY_PIPE_COMPLIANCE_NR1=pipe-id-nr1
PIPEFY_PIPE_COMPLIANCE_LGPD=pipe-id-lgpd
PIPEFY_PIPE_COMPLIANCE_EU_AI_ACT=pipe-id-eu-ai-act
```

## 5. Endpoints da API

| Metodo | Path | Descricao |
|--------|------|-----------|
| POST | `/pipefy/webhook` | Recebe eventos Pipefy |
| POST | `/pipefy/run-check` | Executa check de compliance em card |
| GET | `/pipefy/subscribe` | Ativa assinatura para organizacao |
| GET | `/pipefy/plans` | Lista planos |

## 6. Fluxo de Uso

1. Instala o app AION no Pipefy Ecosystem
2. Adiciona o Pipe "AION Compliance" ao seu organization
3. Cria um card no Pipe com os dados da empresa
4. O webhook dispara e o AION executa o check de compliance
5. Resultado é escrito de volta no card

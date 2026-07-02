# AppSumo — Setup Guide

## 1. Criar Conta de Fornecedor

1. Acesse https://appsumo.com/sell/
2. Crie uma conta de fornecedor (vendor)
3. Preencha perfil da empresa (Global Match Engenharia)

## 2. Criar Deal

No AppSumo Vendor Dashboard:

- **Product Name:** AION Compliance
- **Tagline:** 106 agentes de IA para compliance regulatorio
- **Description:** NR-1, LGPD, EU AI Act, CSRD, DORA, NIS2, SOC2, ISO27001
- **Category:** "SaaS" → "Compliance" / "AI"

### Tiers de Preco Sugeridos

| Tier | Internal Plan | Preco AppSumo | Preco Original |
|------|--------------|---------------|----------------|
| Tier 1 (Starter) | `compliance_essencial` | $49 | $149/mo |
| Tier 2 (Growth) | `regulatory_pro` | $149 | $379/mo |
| Tier 3 (Ultimate) | `full_suite` | $299 | $4,999/mo |

## 3. Configurar Webhook

No AppSumo Vendor Dashboard:

- **Webhook URL:** `https://engenheiro-producao-ai.onrender.com/appsumo/webhook`
- **Secret:** Gerar e configurar como `APPSUMO_WEBHOOK_SECRET` no Render

## 4. Endpoints da API de License

| Metodo | Path | Descricao |
|--------|------|-----------|
| POST | `/appsumo/webhook` | Recebe eventos activate/refund/cancel |
| POST | `/appsumo/license/activate` | Ativa license key do AppSumo |
| POST | `/appsumo/license/validate` | Valida license key |
| GET | `/appsumo/plans` | Lista tiers AppSumo |

## 5. Fluxo do Usuario

1. Usuario compra no AppSumo
2. AppSumo envia webhook `activate` com `plan_id` e `activation_email`
3. AION gera license key e ativa assinatura
4. Usuario faz POST `/appsumo/license/activate` com a license key
5. Usuario acessa o dashboard com acesso vitalicio (lifetime deal)

## 6. Configurar no Render

```bash
APPSUMO_WEBHOOK_SECRET=seu-webhook-secret
```

## 7. Testar

```bash
# Simular ativacao AppSumo
curl -X POST "https://engenheiro-producao-ai.onrender.com/appsumo/webhook" \
  -H "Content-Type: application/json" \
  -H "x-appsumo-signature: sha256=..." \
  -d '{"action":"activate","plan_id":"aion_compliance_tier1","uuid":"test-uuid-123","activation_email":"cliente@exemplo.com"}'
```

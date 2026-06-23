# 🏗️ EcoSystem AEC + Regulatory — 21 Agentes de IA

**Projeto:** Engenheiro de Produção AI
**Proprietário:** Cristiano Arruda | Global Match Engenharia de Produção | CREA-SP 5071200171
**Versão:** 2.1.0
**LLM Core:** DeepSeek-V4-Flash (API OpenAI compatible)
**Framework:** Python + FastAPI + A2A Protocol

---

## 📁 Estrutura do Projeto

```
engenheiro-producao-ai/
├── AGENTS.md                    # Documentação dos agentes (este arquivo)
├── config.yaml                  # Configuração central (agentes, planos, marketplaces)
├── requirements.txt             # Dependências Python
├── Dockerfile                   # Containerização
├── docker-compose.yml           # Orquestração Docker
├── render.yaml                  # Deploy Render.com
├── pytest.ini                   # Configuração de testes
├── .env                         # Variáveis de ambiente (API keys)
├── .env.example                 # Template de variáveis
│
├── src/
│   ├── main.py                  # Entrypoint CLI
│   ├── orchestrator.py          # Orquestrador central (gerencia 21 agentes)
│   ├── config.py                # Settings (carrega config.yaml + .env)
│   ├── cross_selling.py         # Lógica de cross-selling entre agentes
│   │
│   ├── agents/                  # ⬅ 21 agentes implementados
│   │   ├── __init__.py          # Exports de todos os agentes
│   │   ├── spec_analyst.py
│   │   ├── procurement.py
│   │   ├── inventory.py
│   │   ├── logistics.py
│   │   ├── field_execution.py
│   │   ├── bim_coordinator.py
│   │   ├── requirements_analyst.py
│   │   ├── engineering_assistant.py
│   │   ├── work_synopsis.py
│   │   ├── photo_intelligence.py
│   │   ├── rfi_creation.py
│   │   ├── compliance.py
│   │   ├── diagnostic.py
│   │   ├── monitoring.py
│   │   ├── nr1_psicossocial.py
│   │   ├── tributario_cbs_ibs.py
│   │   ├── lgpd_operacional.py
│   │   ├── esg_ifrs.py
│   │   ├── inventario_carbono.py
│   │   ├── escopo3_fornecedores.py
│   │   ├── canal_denuncias.py
│   │   ├── igualdade_salarial.py
│   │   └── compliance_anticorrupcao.py
│   │
│   ├── api/
│   │   └── deepseek_client.py   # Cliente DeepSeek API
│   │
│   ├── database/
│   │   └── supabase_client.py   # Conexão Supabase/PostgreSQL
│   │
│   ├── monetization/
│   │   ├── plans.py             # 9 planos de assinatura
│   │   └── stripe_client.py     # Integração Stripe
│   │
│   ├── a2a_bridge/              # Protocolo Agent-to-Agent
│   │   ├── agent_cards.py       # 21 skills no AgentCard
│   │   ├── executors.py         # Executor A2A para todos os agentes
│   │   ├── setup.py             # Montagem das rotas A2A
│   │   └── monetization.py      # Verificação de assinatura
│   │
│   ├── governance/
│   │   ├── policy_engine.py     # Motor de políticas
│   │   ├── critic_agent.py      # Agente crítico (revisão)
│   │   ├── trust_scorer.py      # Pontuação de confiança
│   │   └── rules/               # Regras de governança
│   │
│   └── security/                # Segurança
│
├── app/
│   ├── main.py                  # FastAPI app (rotas REST)
│   └── routers/                 # Rotas por dominio
│       ├── agents.py
│       ├── subscriptions.py
│       ├── cross_selling.py
│       ├── health.py
│       ├── pgrs.py
│       ├── security.py
│       ├── acp_checkout.py
│       ├── aws_marketplace.py
│       ├── google_marketplace.py
│       └── oracle_marketplace.py
│
├── dashboard/portal/            # Portal do cliente
├── templates/                   # Templates estáticos
├── tests/                       # Testes (51 testes, todos passando)
└── scripts/                     # Scripts auxiliares
```

---

## 🧠 Grupo 1: Núcleo AEC (Agentes #1 a #5)

| # | ID | Agente | Descrição | Preço |
|---|----|--------|-----------|-------|
| 1 | `spec_analyst` | Spec Analyst | Análise de especificações técnicas, extrai requisitos, sinaliza contradições | R$ 997/mês |
| 2 | `procurement` | Procurement | Compras e pedidos automáticos, compara cotações, gera requisições | R$ 597/mês |
| 3 | `inventory` | Inventory | Estoque em tempo real, identifica escassez, sugere substitutos | R$ 797/mês |
| 4 | `logistics` | Logistics | Logística e rastreamento, problemas de entrega, notas fiscais | R$ 797/mês |
| 5 | `field_execution` | Field Execution | Traduz BIM em RA, guia trabalhadores, reduz retrabalho | R$ 1.497/mês |

## 🛠️ Grupo 2: Agentes Especializados (Agentes #6 a #9)

| # | ID | Agente | Descrição | Preço |
|---|----|--------|-----------|-------|
| 6 | `bim_coordinator` | BIM Coordinator | Cria elementos 3D via texto, clash detection, raciocínio espacial | R$ 897/mês |
| 7 | `requirements_analyst` | Requirements Analyst | Análise de qualidade de requisitos contra padrões | R$ 697/mês |
| 8 | `engineering_assistant` | Engineering Assistant | Assistente conversacional, busca semântica, sumarização | R$ 497/mês |
| 9 | `work_synopsis` | Work Synopsis | Resumo de tarefas e defeitos, captura contexto e riscos | R$ 597/mês |

## ⚖️ Grupo 3: Conformidade AEC (Agentes #10 a #12)

| # | ID | Agente | Descrição | Preço |
|---|----|--------|-----------|-------|
| 10 | `photo_intelligence` | Photo Intelligence | Análise visual de obras, detecção de riscos EPI | R$ 797/mês |
| 11 | `rfi_creation` | RFI Creation | Criação automática de RFIs, busca em especificações | R$ 697/mês |
| 12 | `compliance` | Compliance Agent | Gestão de conformidade PGRS/PGRSS, alertas legais | R$ 897/mês |

## 📋 Grupo 4: Agentes Regulatórios (Agentes #13 a #21)

| # | ID | Agente | Norma | Descrição | Preço |
|---|----|--------|-------|-----------|-------|
| 13 | `nr1_psicossocial` | NR-1 Psicossocial | Portaria MTE 1.419/2024 | Inventário de riscos psicossociais (FRPRT), plano de ação, relatórios | R$ 390–1.390/mês |
| 14 | `tributario_cbs_ibs` | Tributário CBS/IBS | LC 214/2025 | Classificação NCM, DeRE, simulação de impacto fiscal | R$ 390–3.900/mês |
| 15 | `lgpd_operacional` | LGPD Operacional | Lei 13.709/2018 | RoPA, mapeamento de dados, conformidade ANPD | R$ 290–990/mês |
| 16 | `esg_ifrs` | ESG IFRS S1/S2 | Res. CVM 193/2023 | Diagnóstico ESG, relatórios IFRS, resposta a questionários | R$ 490–2.490/mês |
| 17 | `inventario_carbono` | Inventário Carbono | Lei 15.042/2024 | Cálculo Escopo 1/2, GHG Protocol, SBCE | R$ 890–4.900/mês |
| 18 | `escopo3_fornecedores` | Escopo 3 Fornecedores | SBCE + CBAM + IFRS S2 | Rastreabilidade de cadeia, 15 categorias GHG | R$ 690–3.490/mês |
| 19 | `canal_denuncias` | Canal de Denúncias | Lei 14.457/2022 | Canal omnichannel, triagem, investigação, relatórios CIPA | R$ 290–990/mês |
| 20 | `igualdade_salarial` | Igualdade Salarial | Lei 14.611/2023 | Análise de equidade, relatório MTE, diversidade | R$ 490–1.490/mês |
| 21 | `compliance_anticorrupcao` | Compliance Anticorrupção | Lei 12.846/2013 | Programa de integridade, código de ética, due diligence | R$ 390–1.490/mês |

---

## 💳 Planos de Assinatura

| Plano | ID | Agentes | Preço |
|-------|----|---------|-------|
| Starter | `starter` | #1 Spec Analyst | R$ 997/mês |
| Professional | `professional` | #1 + #2 + #3 | R$ 2.391/mês |
| Enterprise | `enterprise` | #1 a #5 | R$ 4.685/mês |
| Full Suite | `full_suite` | Todos os 21 agentes | R$ 9.497/mês |
| Compliance Pack | `compliance_pack` | #10 + #11 + #12 | R$ 2.391/mês |
| Regulatory Starter | `regulatory_starter` | #13 + #15 | R$ 590/mês |
| Regulatory Professional | `regulatory_professional` | #13, #15, #19, #20, #21 | R$ 1.490/mês |
| Regulatory Full | `regulatory_full` | #13 a #21 (9 agentes) | R$ 3.490/mês |
| ESG + Carbono | `esg_carbon_pack` | #16 + #17 + #18 | R$ 2.490/mês |

---

## 🔄 Cross-Selling Chain

```
AEC: #1 Spec Analyst → #2 Procurement → #3 Inventory → #4 Logistics → #5 Field Execution
ESP: #6 BIM → #7 Requirements → #8 Assistant → #9 Synopsis
CON: #10 Photo → #11 RFI → #12 Compliance
REG: #13 NR-1 → #15 LGPD → #19 Denúncias → #20 Igualdade → #21 Anticorrupção
     #14 Tributário → #16 ESG → #17 Carbono → #18 Escopo 3
```

---

## ☁️ Infraestrutura

| Componente | Tecnologia |
|-----------|-----------|
| LLM Core | DeepSeek-V4-Flash (API OpenAI compatible) |
| API Framework | FastAPI + Uvicorn |
| Orquestração | n8n (self-hosted) / LangChain |
| Banco de dados | Supabase (PostgreSQL) + Pinecone (vetorial) |
| Pagamentos | Stripe + Abacatepay (PIX) |
| Email | Brevo |
| Protocolo A2A | Google Agent-to-Agent SDK |
| Hospedagem | Render.com / Google Cloud / Oracle Cloud |
| Containers | Docker + docker-compose |

## 🏪 Marketplaces

| Plataforma | Status |
|-----------|--------|
| Google Cloud Marketplace | ✅ Ativo |
| Microsoft Marketplace | ✅ Ativo (API v2 + 21 agentes) |
| Salesforce AgentExchange | ✅ Ativo |
| AWS Marketplace | 🔧 Configurado (inativo) |
| Oracle Cloud Marketplace | 🔧 Configurado (inativo) |
| MuleRun | ✅ Ativo |
| AI Agents Directory | ✅ Ativo |
| NexusGPT | ✅ Ativo |
| SwarmSync (A2A) | 🔧 Em desenvolvimento |
| OpenStall (A2A) | 🔧 Em desenvolvimento |

---

## 🧪 Testes

**Status:** 51/51 testes passando ✅

- `tests/test_orchestrator.py` — Inicialização, health check, run_agent, workflow
- `tests/test_plans.py` — Estrutura de planos, preços, agentes por plano
- `tests/test_cross_selling.py` — Upgrade paths, upsell, agent names
- `tests/test_agents/*` — Testes unitários de agentes individuais

---

## 🚀 Comandos

```bash
# Rodar localmente
python src/main.py --config config.yaml

# Modo debug
python src/main.py --config config.yaml --debug

# Deploy Docker
docker build -t engenheiro-producao-ai .
docker-compose up -d

# Testes
pytest tests/ -q

# Testar agente específico
python -c "from src.agents.nr1_psicossocial import NR1PsicossocialAgent; print('OK')"
```

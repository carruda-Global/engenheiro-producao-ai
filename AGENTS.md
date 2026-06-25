# 🏗️ EcoSystem AEC + Regulatory — 30 Agentes de IA

**Projeto:** Engenheiro de Produção AI
**Proprietário:** Cristiano Arruda | Global Match Engenharia de Produção | CREA-SP 5071200171
**Versão:** 3.0.0
**LLM Core:** DeepSeek-V4-Flash (API OpenAI compatible) + Gemini (agentes sensíveis LGPD)
**Framework:** Python + FastAPI + A2A Protocol

---

## Status dos Agentes por Fase de Lançamento

| Status | Significado |
|--------|-------------|
| `active` | Publicado e disponível em self-serve |
| `scheduled_q4_2026` | Lançamento previsto Q4 2026 |
| `scheduled_q1_2027` | Lançamento previsto Q1 2027 |
| `co-sell` | Disponível apenas via co-sell com parceiros |

## LLM Tier

| Tier | LLM | Agentes |
|------|-----|---------|
| `default` | DeepSeek-V4-Flash | Agentes AEC, ESG/Carbono, Microsoft |
| `sensitive` | Gemini | Agentes com dados pessoais sensíveis (NR-1, LGPD, Denúncias, Igualdade Salarial, Anticorrupção) |

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

## 🧠 Grupo 1: Núcleo AEC (Agentes #1 a #5) — Canal: Google Cloud

| # | ID | Agente | Descrição | Preço | Status | Canais | LLM Tier |
|---|----|--------|-----------|-------|--------|--------|----------|
| 1 | `spec_analyst` | Spec Analyst | Análise de especificações técnicas, extrai requisitos, sinaliza contradições | R$ 997/mês | active | google | default |
| 2 | `procurement` | Procurement | Compras e pedidos automáticos, compara cotações, gera requisições | R$ 597/mês | active | google | default |
| 3 | `inventory` | Inventory | Estoque em tempo real, identifica escassez, sugere substitutos | R$ 797/mês | active | google | default |
| 4 | `logistics` | Logistics | Logística e rastreamento, problemas de entrega, notas fiscais | R$ 797/mês | active | google | default |
| 5 | `field_execution` | Field Execution | Traduz BIM em RA, guia trabalhadores, reduz retrabalho | R$ 1.497/mês | active | google | default |

## 🛠️ Grupo 2: Agentes Especializados (Agentes #6 a #9) — Canal: Google Cloud

| # | ID | Agente | Descrição | Preço | Status | Canais | LLM Tier |
|---|----|--------|-----------|-------|--------|--------|----------|
| 6 | `bim_coordinator` | BIM Coordinator | Cria elementos 3D via texto, clash detection, raciocínio espacial | R$ 897/mês | active | google | default |
| 7 | `requirements_analyst` | Requirements Analyst | Análise de qualidade de requisitos contra padrões | R$ 697/mês | active | google | default |
| 8 | `engineering_assistant` | Engineering Assistant | Assistente conversacional, busca semântica, sumarização | R$ 497/mês | active | google | default |
| 9 | `work_synopsis` | Work Synopsis | Resumo de tarefas e defeitos, captura contexto e riscos | R$ 597/mês | active | google | default |

## ⚖️ Grupo 3: Conformidade AEC (Agentes #10 a #12) — Canal: Google Cloud

| # | ID | Agente | Descrição | Preço | Status | Canais | LLM Tier |
|---|----|--------|-----------|-------|--------|--------|----------|
| 10 | `photo_intelligence` | Photo Intelligence | Análise visual de obras, detecção de riscos EPI | R$ 797/mês | active | google | default |
| 11 | `rfi_creation` | RFI Creation | Criação automática de RFIs, busca em especificações | R$ 697/mês | active | google | default |
| 12 | `compliance` | Compliance Agent | Gestão de conformidade PGRS/PGRSS, alertas legais | R$ 897/mês | active | google | default |

## 📋 Grupo 4: Agentes Regulatórios (Agentes #13 a #21) — Canais: Google + Salesforce + Microsoft

| # | ID | Agente | Norma | Descrição | Preço | Status | Canais | LLM Tier |
|---|----|--------|-------|-----------|-------|--------|--------|----------|
| 13 | `nr1_psicossocial` | NR-1 Psicossocial | Portaria MTE 1.419/2024 | Inventário de riscos psicossociais (FRPRT), plano de ação, relatórios | R$ 390–1.390/mês | active | google, salesforce, microsoft | sensitive |
| 14 | `tributario_cbs_ibs` | Tributário CBS/IBS | LC 214/2025 | Classificação NCM, DeRE, simulação de impacto fiscal | R$ 390–3.900/mês | scheduled_q4_2026 | google, salesforce | default |
| 15 | `lgpd_operacional` | LGPD Operacional | Lei 13.709/2018 | RoPA, mapeamento de dados, conformidade ANPD | R$ 290–990/mês | active | google, salesforce, microsoft | sensitive |
| 16 | `esg_ifrs` | ESG IFRS S1/S2 | Res. CVM 193/2023 | Diagnóstico ESG, relatórios IFRS, resposta a questionários | R$ 490–2.490/mês | scheduled_q1_2027 | google, oracle | default |
| 17 | `inventario_carbono` | Inventário Carbono | Lei 15.042/2024 | Cálculo Escopo 1/2, GHG Protocol, SBCE | R$ 890–4.900/mês | scheduled_q1_2027 | google, oracle | default |
| 18 | `escopo3_fornecedores` | Escopo 3 Fornecedores | SBCE + CBAM + IFRS S2 | Rastreabilidade de cadeia, 15 categorias GHG | R$ 690–3.490/mês | scheduled_q1_2027 | google, oracle | default |
| 19 | `canal_denuncias` | Canal de Denúncias | Lei 14.457/2022 | Canal omnichannel, triagem, investigação, relatórios CIPA | R$ 290–990/mês | active | google, salesforce, microsoft | sensitive |
| 20 | `igualdade_salarial` | Igualdade Salarial | Lei 14.611/2023 | Análise de equidade, relatório MTE, diversidade | R$ 490–1.490/mês | active | google, salesforce, microsoft | sensitive |
| 21 | `compliance_anticorrupcao` | Compliance Anticorrupção | Lei 12.846/2013 | Programa de integridade, código de ética, due diligence | R$ 390–1.490/mês | scheduled_q4_2026 | google, salesforce, microsoft | sensitive |

## 🪟 Grupo 5: Agentes Microsoft (Agentes #22 a #27) — Co-sell via MSPs

| # | ID | Agente | Descrição | Preço | Status | Canais | LLM Tier |
|---|----|--------|-----------|-------|--------|--------|----------|
| 22 | `regulatory_analyst` | Regulatory Analyst | Análise de contratos e documentos legais via SharePoint/OneDrive, riscos LGPD/NR-1/ESG | R$ 997/mês | co-sell | microsoft | default |
| 23 | `compliance_pm` | Compliance PM | Gestão de projetos de compliance (PGRS, Carbono, Igualdade), tarefas no Planner | R$ 797/mês | co-sell | microsoft | default |
| 24 | `channel_agent` | Channel Agent Regulatório | Monitoramento de canais Teams, detecção de riscos trabalhistas/tributários | R$ 597/mês | co-sell | microsoft | default |
| 25 | `knowledge_agent` | Knowledge Agent | Indexação de documentos SharePoint com RAG, busca inteligente | R$ 697/mês | co-sell | microsoft | default |
| 26 | `facilitator_agent` | Facilitator Agent | Facilitação de reuniões de compliance, atas, minutas, tarefas no Planner | R$ 497/mês | co-sell | microsoft | default |
| 27 | `dev_experience` | Dev Experience Agent | Automação de PRs e code reviews, conformidade LGPD em código | R$ 897/mês | co-sell | microsoft | default |

---

## 💳 Planos de Assinatura — 6 planos visíveis nos listings

| Plano | ID | Agentes | Preço | Posição |
|-------|----|---------|-------|---------|
| Compliance Essencial | `compliance_essencial` | #13 NR-1 + #15 LGPD | R$ 590/mês | 🏆 Mais popular — porta de entrada |
| Regulatory Pro | `regulatory_pro` | #13, #15, #19, #20, #21 | R$ 1.490/mês | Upsell natural pós-entrada |
| Tributário CBS/IBS Starter | `tributario_entrada` | #14 | R$ 390/mês | Q4 2026 (LC 214/2025) |
| ESG + Carbono PME | `esg_carbon` | #16 + #17 + #18 | R$ 2.490/mês | Q1 2027 (IFRS S1/S2, SBCE) |
| Microsoft Compliance Pack | `microsoft_pack` | #22 a #27 | R$ 4.482/mês | Co-sell com MSPs |
| Cross-Sell Harmony | `cross_sell_harmony` | #N1 Onboarding | R$ 490/mês | Entrada jornada A |
| Atendimento Plus | `atendimento_plus` | #N2 Atendimento PT-BR | R$ 390/mês | Upsell suporte |
| Conciliação Pro | `conciliacao_pro` | #N3 Conciliação Financeira | R$ 790/mês | Upsell financeiro |
| Full Suite | `full_suite` | Todos os 30 agentes | R$ 9.497/mês | Âncora de percepção de valor |

### Planos desativados da vitrine (mantidos no Stripe para assinaturas ativas)
- `starter` (Spec Analyst isolado)
- `professional` (3 agentes AEC)
- `enterprise` (5 agentes AEC)
- `compliance_pack` (PGRS/PGRSS — canal Google exclusivo)
- `regulatory_full` (absorvido pelo Regulatory Pro + ESG separados)

---

## 🔄 Cross-Selling Chain

```
AEC: #1 Spec Analyst → #2 Procurement → #3 Inventory → #4 Logistics → #5 Field Execution
ESP: #6 BIM → #7 Requirements → #8 Assistant → #9 Synopsis
CON: #10 Photo → #11 RFI → #12 Compliance
REG: #13 NR-1 → #15 LGPD → #19 Denúncias → #20 Igualdade → #21 Anticorrupção
     #14 Tributário → #16 ESG → #17 Carbono → #18 Escopo 3
MST: #22 Regulatory → #23 PM → #24 Channel → #25 Knowledge → #26 Facilitator → #27 DevEx
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

| Plataforma | Status | Produto de entrada | Observação |
|-----------|--------|-------------------|------------|
| Google Cloud Marketplace | ✅ Foco total — Q3 2026 | Compliance Essencial R$ 590 | Canal primário — não diluir esforço |
| Microsoft Marketplace | ✅ Otimizado (self-serve) | Compliance Essencial R$ 590 | Apenas bundle de entrada em self-serve |
| Salesforce AgentExchange | ✅ Otimizado (integração) | Compliance Essencial R$ 590 | Gancho de integração Salesforce obrigatório |
| Oracle Cloud Marketplace | ⏸ Pausado | — | Ativar Q1 2027 com ESG/Carbono |
| AWS Marketplace | ⏸ Pausado | — | Ativar só com ARR > R$ 3M |
| SAP AI Agent Hub | 🎯 Avaliando entrada | CBS/IBS R$ 390 | Janela LC 214/2025, €100M fundo ISV ativo |
| MuleRun | ✅ Manter | — | Custo zero, awareness |
| NexusGPT | ✅ Manter | — | Custo zero, awareness |
| AI Agents Directory | ✅ Manter | — | Custo zero, awareness |
| SwarmSync (A2A) | ⏸ Pausado | — | Protocolo A2A ainda imaturo |
| OpenStall (A2A) | ⏸ Pausado | — | Protocolo A2A ainda imaturo |

---

## 🆕 Grupo 6: Cross-Sell — Agentes de Jornada (Agentes #N1 a #N3) — Canais: Microsoft + Salesforce

| # | ID | Agente | Descrição | Preço | Status | Canais | LLM Tier |
|---|----|--------|-----------|-------|--------|--------|----------|
| N1 | `onboarding_funcionarios` | Onboarding de Funcionários | Automatiza admissão, contratos, checklist de documentos, provisionamento de acessos (email, Teams, sistemas), eSocial | R$ 490/mês | active | microsoft, salesforce | default |
| N2 | `atendimento_cliente_ptbr` | Atendimento ao Cliente PT-BR | Resolve tickets L1 via WhatsApp + Teams em português brasileiro. Cobre dúvidas, status, agendamento, FAQs | R$ 390/mês | active | microsoft, salesforce | default |
| N3 | `conciliacao_financeira` | Conciliação Financeira | Automatiza fechamento mensal: concilia NFs com extratos, faturas de cartão e boletos. Identifica divergências | R$ 790/mês | active | microsoft, salesforce | default |

## 🔄 Jornadas de Cross-Sell Vertical

### Jornada A — Entrada RH → Financeiro → Compliance (Microsoft + Salesforce)
Onboarding → NR-1 → Igualdade Salarial → LGPD → Denúncias → Atendimento → Conciliação
**LTV potencial:** R$ 3.130/mês | **Multiplicador:** 6,4x

### Jornada B — Entrada Fiscal → ESG → Carbono (Google Cloud)
Tributário CBS/IBS → Anticorrupção → ESG → Carbono → Escopo 3 → LGPD → Conciliação → Atendimento
**LTV potencial:** R$ 4.320/mês | **Multiplicador:** 11x

### Jornada C — Entrada AEC → Regulatório → Microsoft (Co-sell)
Compliance PGRS → NR-1 → Denúncias → Regulatory → Onboarding → Atendimento → Conciliação
**LTV potencial:** R$ 4.941/mês | **Multiplicador:** 5,5x

## 🧪 Testes

**Status:** 75/75 testes passando ✅

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

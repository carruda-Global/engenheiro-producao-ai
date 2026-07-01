import os
import uuid
import logging

from fastapi import FastAPI, HTTPException, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel

from src.config import Settings, get_settings
from src.orchestrator import Orchestrator as HMASOrchestrator
from src.monetization.plans import PLANS, get_plan
from src.monitoring.agent_dashboard import AgentDashboard
from src.security.circuit_breaker import CircuitBreaker
try:
    from src.database.postgres_client import init_pool, close_pool, get_conn
except ImportError:
    init_pool = close_pool = get_conn = None
try:
    from src.messaging.producer import init_producer, close_producer, enqueue_agent_task
except ImportError:
    init_producer = close_producer = enqueue_agent_task = None

from app.routers.salesforce_marketplace import router as salesforce_router
from app.routers.subscriptions import router as subscriptions_router
from app.routers.health import router as health_router
from app.routers.aip_security import router as aip_router
from app.routers.microsoft_marketplace import router as microsoft_router
from app.routers.cross_selling import router as cross_selling_router
from app.routers.google_marketplace import router as google_router
from app.routers.aws_marketplace import router as aws_router
from app.routers.leads import router as leads_router
from app.routers.stripe_app import router as stripe_app_router
from app.routers.privacy import router as privacy_router
from app.routers.stripe_webhook import router as stripe_webhook_router
from app.routers.governance import router as governance_router
from app.routers.bridge import router as bridge_router
from app.routers.code_review import router as code_review_router
from app.routers.physical_ai import router as physical_ai_router
from app.routers.checkout import router as checkout_router
from src.fulfillment.webhooks.stripe_fulfillment import router as fulfillment_router
from src.api.routes.status import router as status_router
from src.api.middleware.privacy import PrivacyConsentMiddleware

from app.routers.sales_agent_chat import router as sales_agent_chat_router
from src.agents.visitor_id_agent import router as visitor_id_router
from src.agents.seo_content_agent import router as seo_agent_router
from src.agents.seo_pages_router import router as seo_pages_router
from src.agents.eu_ai_act_agent import router as eu_ai_act_router
from src.agents.lfpdppp_agent import router as lfpdppp_router
from src.agents.ley1581_agent import router as ley1581_router
from src.agents.sdr_backoffice_agent import router as sdr_backoffice_router
from src.agents.usage_billing import router as usage_billing_router
from app.routers.office_addin import router as office_addin_router
from app.routers.office_addin_commands import router as office_addin_commands_router
from src.agents.india_multilingual_agent import router as india_agent_router
from src.agents.uae_government_agent import router as uae_agent_router
from src.agents.csrd_reporting_agent import router as csrd_router
from src.agents.dora_compliance_agent import router as dora_router
from src.agents.soc2_agent import router as soc2_router
from src.agents.iso27001_agent import router as iso27001_router
from src.agents.nis2_agent import router as nis2_router
from src.agents.outbound_sdr_agent import router as outbound_sdr_router
from src.agents.content_syndication_agent import router as syndication_router
from src.agents.partnership_agent import router as partnership_router
from src.agents.vendor_risk_agent import router as vendor_risk_router
from src.agents.board_reporting_agent import router as board_report_router
from src.agents.ma_due_diligence_agent import router as ma_diligence_router
from src.agents.regulatory_monitor_agent import router as reg_monitor_router
from src.agents.contract_risk_agent import router as contract_risk_router
from src.agents.whistleblower_agent import router as whistleblower_router
from src.agents.zapier_integration_agent import router as zapier_router
from src.agents.dashboard_agent import router as dashboard_router
from src.agents.social_auto_agent import router as social_auto_router
from src.agents.directory_submission_agent import router as directories_router
from src.agents.review_nurture_agent import router as nurture_router
from src.agents.pmoc_seo_agent import router as pmoc_seo_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from app.routers.oracle_marketplace import router as oracle_router
except ImportError:
    oracle_router = APIRouter()
    logger.warning("Oracle router nao carregado (oci nao instalado)")

try:
    settings = Settings()
    config_errors = settings.validate()
    if config_errors:
        logger.warning("Configuracao incompleta no startup: %s", config_errors)
except Exception as e:
    logger.warning("Configuracao parcial no startup, usando defaults: %s", e)
    settings = Settings.__new__(Settings)
    settings.app_env = os.getenv("APP_ENV", "development")
    settings.base_url = os.getenv("BASE_URL", "https://engenheiro-producao-ai.onrender.com")
    settings.agents_config = {}
    settings.llm_routing_config = {}

_is_production = settings.app_env == "production"
cors_origins = [settings.base_url] if _is_production else ["*"]

app = FastAPI(
    title="SallesJam - Multi-Market Sales Intelligence",
    description="SallesJam: IA multi-mercado para vendas e compliance (Brasil, EUA, México, Colômbia, Argentina)",
    version="7.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=_is_production,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(PrivacyConsentMiddleware)

orchestrator = HMASOrchestrator(settings)
dashboard = AgentDashboard()
circuit_breaker = CircuitBreaker(threshold=5, reset_seconds=60)


@app.on_event("startup")
async def startup():
    if init_pool:
        await init_pool()
    if init_producer:
        await init_producer()
    logger.info("Inicializando H-MAS com 59 agentes...")
    await orchestrator.initialize()
    logger.info("Sistema pronto. 59/59 agentes ativos.")


@app.on_event("shutdown")
async def shutdown():
    if close_producer:
        await close_producer()
    if close_pool:
        await close_pool()


class AgentExecuteRequest(BaseModel):
    tenant_id: str = "default"
    agent_id: str
    task_type: str = "execute"
    payload: dict = {}


@app.post("/api/agents/execute")
async def execute_task(request: AgentExecuteRequest):
    task_id = str(uuid.uuid4())

    try:
        async with get_conn() as conn:
            await conn.execute(
                """
                INSERT INTO agent_executions
                    (id, tenant_id, agent_id, task_type, status, input_summary)
                VALUES ($1, $2, $3, $4, 'queued', $5)
                """,
                task_id,
                request.tenant_id,
                request.agent_id,
                request.task_type,
                str(request.payload)[:500],
            )
    except Exception:
        logger.warning("Banco indisponivel, executando síncrono")
        result = await orchestrator.execute_task(request.dict(), user_id=request.tenant_id)
        return result

    try:
        async with get_conn() as conn:
            row = await conn.fetchrow(
                "SELECT cluster FROM agent_registry WHERE id = $1 AND status = 'active'",
                request.agent_id,
            )
    except Exception:
        row = None

    if row:
        await enqueue_agent_task(
            task_id=task_id,
            tenant_id=request.tenant_id,
            agent_id=request.agent_id,
            cluster=row["cluster"],
            task_type=request.task_type,
            payload=request.payload,
        )
        return {
            "task_id": task_id,
            "status": "queued",
            "poll_url": f"/api/tasks/{task_id}",
            "message": "Task enfileirada. Use poll_url para acompanhar o resultado.",
        }

    result = await orchestrator.execute_task(request.dict(), user_id=request.tenant_id)
    return result


@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    try:
        async with get_conn() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM agent_executions WHERE id = $1", task_id,
            )
        if row:
            return dict(row)
    except Exception:
        pass
    raise HTTPException(status_code=404, detail="Task nao encontrada")


app.include_router(salesforce_router, prefix="/salesforce", tags=["salesforce"])
app.include_router(subscriptions_router, prefix="/api/subscriptions", tags=["subscriptions"])
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(aip_router)
app.include_router(microsoft_router)
app.include_router(cross_selling_router, prefix="/api/cross-sell", tags=["cross-sell"])
app.include_router(google_router, prefix="/google", tags=["google"])
app.include_router(aws_router, prefix="/aws", tags=["aws"])
app.include_router(oracle_router, prefix="/oracle", tags=["oracle"])
app.include_router(leads_router)
app.include_router(stripe_app_router)
app.include_router(privacy_router)
app.include_router(stripe_webhook_router)
app.include_router(governance_router)


@app.get("/suporte", response_class=HTMLResponse)
async def support_page():
    return HTMLResponse(content="""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>Suporte - SallesJam</title>
<style>body{font-family:sans-serif;max-width:600px;margin:40px auto;padding:20px;background:#0C1322;color:#e2e8f0}h1{color:#00C36B}a{color:#00C36B}</style>
</head>
<body>
<h1>Suporte SallesJam</h1>
<p><strong>Email:</strong> cristiano.arruda@global-engenharia.com</p>
<p><strong>Telefone:</strong> (11) 99479-8464</p>
<p><strong>Documentacao:</strong> <a href="https://global-engenharia.com/ecosystem">global-engenharia.com/ecosystem</a></p>
<p style="color:#64748b;font-size:12px">Respondemos em ate 24h uteis.</p>
</body>
</html>""")


@app.get("/googleCWytB8JSZT1X17frcedHEG6ZHBIW4Bj0UnuCXCK0UrI.html")
async def google_verify_new2():
    return HTMLResponse(content='google-site-verification: googleCWytB8JSZT1X17frcedHEG6ZHBIW4Bj0UnuCXCK0UrI.html')


@app.get("/googlekl673VPS54kpHqZIsCbysRBV0Os6o6x3IiAiJeDVmcY.html")
async def google_verify_new():
    return HTMLResponse(content='google-site-verification: googlekl673VPS54kpHqZIsCbysRBV0Os6o6x3IiAiJeDVmcY.html')


@app.get("/googlef3d8c8be30343045.html")
async def google_verify():
    return HTMLResponse(content="google-site-verification: googlef3d8c8be30343045.html")
app.include_router(bridge_router)
app.include_router(code_review_router)
app.include_router(physical_ai_router)
app.include_router(checkout_router)
app.include_router(fulfillment_router)
app.include_router(status_router)
app.include_router(sales_agent_chat_router)
app.include_router(visitor_id_router)
app.include_router(seo_agent_router)
app.include_router(seo_pages_router)
app.include_router(eu_ai_act_router)
app.include_router(lfpdppp_router)
app.include_router(ley1581_router)
app.include_router(sdr_backoffice_router)
app.include_router(usage_billing_router)
app.include_router(office_addin_router)
app.include_router(india_agent_router)
app.include_router(uae_agent_router)
app.include_router(csrd_router)
app.include_router(dora_router)
app.include_router(soc2_router)
app.include_router(iso27001_router)
app.include_router(nis2_router)
app.include_router(outbound_sdr_router)
app.include_router(syndication_router)
app.include_router(partnership_router)
app.include_router(vendor_risk_router)
app.include_router(board_report_router)
app.include_router(ma_diligence_router)
app.include_router(reg_monitor_router)
app.include_router(contract_risk_router)
app.include_router(whistleblower_router)
app.include_router(zapier_router)
app.include_router(dashboard_router)
app.include_router(social_auto_router)
app.include_router(directories_router)
app.include_router(nurture_router)
app.include_router(pmoc_seo_router)

def _make_loop(name: str, fn, interval: int):
    """Wraps any async fn into an infinite loop that starts immediately, no warm-up."""
    async def _loop():
        while True:
            try:
                await fn()
                logger.info("[24/7] %s done", name)
            except Exception as e:
                logger.error("[24/7] %s error: %s", name, e)
            await asyncio.sleep(interval)
    return _loop()


@app.on_event("startup")
async def startup_event():
    import asyncio
    import random
    from src.agents.seo_content_agent import SEOContentAgent
    from src.agents.content_syndication_agent import _publish_to_devto, TOPICS
    from src.agents.pmoc_seo_agent import generate_pmoc_pages
    from src.agents.social_auto_agent import auto_job_reddit, auto_job_linkedin_content
    from src.agents.directory_submission_agent import auto_job_directories, auto_job_press_release_distribution, auto_job_regtech_press
    from src.agents.review_nurture_agent import auto_job_nurture_sequence, auto_job_reactivation

    # ── SEO Ecosystem — 40 páginas/dia, roda a cada 6h ──────────────────────
    async def _seo():
        agent = SEOContentAgent()
        for market in ["BR", "US", "MX", "CO", "AR"]:
            try:
                await agent.generate_market_pages(market)
            except Exception as e:
                logger.warning("[24/7] SEO market=%s: %s", market, e)

    # ── Dev.to — 3 artigos/dia, roda a cada 8h ──────────────────────────────
    async def _devto():
        await _publish_to_devto(random.choice(TOPICS))

    # ── SDR — 1000 emails/dia, roda a cada 12h ──────────────────────────────
    async def _sdr():
        try:
            from src.agents.outbound_sdr_agent import send_campaign
            for sector in ["construction_br", "finance_eu", "tech_saas", "manufacturing_eu", "any_eu"]:
                try:
                    await send_campaign({"sector": sector, "limit": 100})
                except Exception as e:
                    logger.warning("[24/7] SDR sector=%s: %s", sector, e)
        except ImportError:
            pass

    # ── Press Release — roda a cada 7 dias ──────────────────────────────────
    async def _pr():
        from src.agents.zapier_integration_agent import generate_press_release
        await generate_press_release({"angle": "86 AI compliance agents — EU AI Act, CSRD, DORA, NIS2"})

    # ── PMOC SEO — 90 páginas em ciclo de 3 batches a cada 12h ─────────────
    _pmoc_cycle = [0]
    _pmoc_batches = [("bairros", 30), ("empresas", 20), ("problemas", 20)]
    async def _pmoc():
        batch, count = _pmoc_batches[_pmoc_cycle[0] % 3]
        result = await generate_pmoc_pages(batch, count)
        logger.info("[24/7] PMOC-SEO: %d páginas (batch=%s)", result["generated"], batch)
        _pmoc_cycle[0] += 1

    JOBS = [
        ("SEO-Ecosystem",    _seo,                          21600),   # 6h
        ("Dev.to",           _devto,                        28800),   # 8h
        ("SDR-Emails",       _sdr,                          43200),   # 12h
        ("Press-Release",    _pr,                           604800),  # 7d
        ("Reddit",           auto_job_reddit,               172800),  # 48h
        ("LinkedIn",         auto_job_linkedin_content,     86400),   # 24h
        ("Directories",      auto_job_directories,          259200),  # 72h
        ("PR-Distribution",  auto_job_press_release_distribution, 1209600),  # 14d
        ("Regtech-Press",    auto_job_regtech_press,            604800),  # 7d
        ("Nurture-Emails",   auto_job_nurture_sequence,     86400),   # 24h
        ("Reactivation",     auto_job_reactivation,         604800),  # 7d
        ("PMOC-SEO",         _pmoc,                         43200),   # 12h
    ]

    for name, fn, interval in JOBS:
        asyncio.create_task(_make_loop(name, fn, interval))

    logger.info("[24/7] %d jobs iniciados — sem calendário, sem intervenção manual", len(JOBS))


static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def root(request: Request):
    ua = request.headers.get("user-agent", "")
    if "Google" in ua or "google" in ua:
        return HTMLResponse(content='<!DOCTYPE html><html><head><meta name="google-site-verification" content="ofHIVuOsmwHY-JSIStSCtLW0Y_UrzJyyf_-HcsyTeGk" /></head><body></body></html>')
    return {
        "service": "SallesJam - Multi-Market Sales Intelligence",
        "version": "7.0.0",
        "status": "operational",
        "agents_total": len(orchestrator.agents),
        "markets": ["BR", "US", "MX", "CO", "AR"],
    }


@app.get("/.well-known/agent-card.json")
async def agent_card():
    return {
        "name": "SallesJam - Multi-Market Sales Intelligence",
        "description": "SallesJam: IA para vendas e compliance em 5 mercados. Brasil (NR-1, LGPD, ESG), EUA (EU AI Act), México (LFPDPPP), Colômbia (Ley 1581), Argentina (SDR/Back-office).",
        "version": "7.0.0",
        "provider": {
            "organization": "Global Engenharia",
            "url": "https://engenheiro-producao-ai.onrender.com",
        },
        "documentationUrl": "https://engenheiro-producao-ai.onrender.com/docs",
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
        },
        "supportedInterfaces": [
            {
                "protocolBinding": "JSONRPC",
                "protocolVersion": "1.0",
                "url": "https://engenheiro-producao-ai.onrender.com/a2a/jsonrpc",
            }
        ],
        "defaultInputModes": ["text"],
        "defaultOutputModes": ["text"],
        "skills": [
            {
                "id": "nr1_psicossocial",
                "name": "NR-1 Psicossocial",
                "description": "Avaliacao de riscos psicossociais conforme NR-1 e elaboracao de planos de acao para conformidade trabalhista brasileira.",
                "tags": ["compliance", "nr1", "regulatory", "brazil", "hr"],
            },
            {
                "id": "lgpd_operacional",
                "name": "LGPD Operacional",
                "description": "Operacionalizacao da LGPD: mapeamento de dados pessoais, elaboracao de politicas de privacidade e gestao de consentimento.",
                "tags": ["lgpd", "privacy", "compliance", "data-protection", "brazil"],
            },
            {
                "id": "esg_ifrs",
                "name": "ESG IFRS S1/S2",
                "description": "Relatorios de sustentabilidade conforme IFRS S1 e S2, inventario de carbono e metas ESG para empresas brasileiras.",
                "tags": ["esg", "sustainability", "carbon", "ifrs", "reporting"],
            },
            {
                "id": "spec_analyst",
                "name": "Analista de Especificacoes Tecnicas",
                "description": "Analisa documentos de engenharia (plantas, memoriais, normas NBR) para extrair requisitos tecnicos e identificar contradicoes.",
                "tags": ["engineering", "aec", "specifications", "nbr", "construction"],
            },
            {
                "id": "bim_coordinator",
                "name": "BIM Coordinator",
                "description": "Coordenacao BIM: deteccao de conflitos, gestao de modelos IFC e relatorios de compatibilizacao para projetos de construcao.",
                "tags": ["bim", "ifc", "construction", "aec", "coordination"],
            },
            {
                "id": "regulatory_analyst",
                "name": "Regulatory Analyst M365",
                "description": "Analise regulatoria integrada ao Microsoft 365: monitora mudancas normativas e gera alertas de conformidade no Teams e SharePoint.",
                "tags": ["microsoft", "m365", "regulatory", "compliance", "teams"],
            },
            {
                "id": "dynamics_sales",
                "name": "Dynamics 365 Sales Agent",
                "description": "Automacao de vendas no Dynamics 365: qualificacao de leads, previsao de receita e gestao de pipeline com IA generativa.",
                "tags": ["dynamics365", "microsoft", "crm", "sales", "erp"],
            },
            {
                "id": "agentforce_sdr",
                "name": "Agentforce SDR",
                "description": "Agente SDR no Salesforce Agentforce: prospecao automatizada, qualificacao de leads e agendamento de reunioes via Einstein AI.",
                "tags": ["salesforce", "agentforce", "sdr", "crm", "sales"],
            },
            {
                "id": "oracle_erp_compliance",
                "name": "Oracle ERP Compliance",
                "description": "Conformidade regulatoria no Oracle Fusion ERP: automacao de obrigacoes fiscais brasileiras (SPED, NF-e, eSocial) integradas ao Oracle.",
                "tags": ["oracle", "erp", "compliance", "fiscal", "brazil"],
            },
            {
                "id": "sap_joule_compliance",
                "name": "SAP Joule Compliance",
                "description": "Agente de compliance no SAP S/4HANA via SAP Joule: auditoria automatizada de processos fiscais e regulatorios brasileiros.",
                "tags": ["sap", "s4hana", "joule", "compliance", "erp"],
            },
        ],
    }


@app.get("/api/status/{tenant_id}")
async def get_status(tenant_id: str):
    return dashboard.get_agent_status(tenant_id)


@app.post("/api/agents/initialize")
async def initialize_agents(data: dict):
    tenant = data.get("tenant", "default")
    clusters = data.get("clusters", ["aec_core", "aec_specialized", "aec_compliance", "regulatory", "microsoft", "cross_sell", "dynamics", "agentforce", "oracle", "sap", "coordination", "intelligence", "tech", "self_improvement"])
    orchestrator.tenant_id = tenant
    await orchestrator.initialize()
    return {
        "status": "initialized",
        "tenant": tenant,
        "clusters": clusters,
        "agents_total": len(orchestrator.agents),
    }


@app.get("/api/agents/{agent_id}/status")
async def get_agent_status(agent_id: str):
    agent = orchestrator.agents.get(agent_id)
    if not agent:
        return {"error": f"Agent {agent_id} not found"}, 404
    return agent.to_dict()


@app.get("/api/agents/health")
async def agents_health():
    statuses = {}
    for agent_id, agent in orchestrator.agents.items():
        statuses[agent_id] = {
            "status": getattr(agent, "status", "initialized"),
            "success_rate": getattr(agent, "success_rate", 1.0),
            "total_tasks": getattr(agent, "total_tasks", 0),
            "avg_response_time": getattr(agent, "avg_response_time", 0.0),
        }
    return {
        "total_agents": len(statuses),
        "agents": statuses,
    }


MCP_SERVERS = {
    "regulatory": {
        "url": "https://engenheiro-producao-ai.onrender.com/mcp/regulatory/sse",
        "tools": ["nr1_psicossocial", "lgpd_operacional", "tributario_cbs_ibs", "canal_denuncias", "igualdade_salarial", "compliance_anticorrupcao", "onboarding_funcionarios", "conciliacao_financeira"],
    },
    "esg": {
        "url": "https://engenheiro-producao-ai.onrender.com/mcp/esg/sse",
        "tools": ["esg_ifrs_diagnostico", "inventario_carbono", "escopo3_fornecedores", "cbam_certificate"],
    },
    "erp": {
        "url": "https://engenheiro-producao-ai.onrender.com/mcp/erp/sse",
        "tools": ["dynamics_sales", "dynamics_finance", "dynamics_hr", "agentforce_sdr", "agentforce_contracts", "oracle_erp_compliance", "oracle_hcm_regulatory", "sap_compliance_bridge", "sap_cbam_export", "powerbi_compliance"],
    },
}


@app.get("/mcp/servers")
async def list_mcp_servers():
    return {"servers": MCP_SERVERS, "total": len(MCP_SERVERS)}


async def _mcp_toolspec_data():
    return {
        "tools": [
            {"name": "nr1_psicossocial", "description": "Avalia riscos psicossociais conforme NR-1 e gera plano de acao para conformidade trabalhista brasileira.", "inputSchema": {"type": "object", "properties": {"empresa": {"type": "string", "description": "Nome da empresa"}, "setor": {"type": "string"}}, "required": ["empresa"]}},
            {"name": "lgpd_operacional", "description": "Mapeia dados pessoais e gera politica de privacidade conforme LGPD brasileira.", "inputSchema": {"type": "object", "properties": {"empresa": {"type": "string"}, "tipo_dados": {"type": "string"}}, "required": ["empresa"]}},
            {"name": "esg_ifrs", "description": "Gera relatorio de sustentabilidade conforme IFRS S1/S2 e calcula inventario de carbono.", "inputSchema": {"type": "object", "properties": {"empresa": {"type": "string"}, "ano_referencia": {"type": "integer"}}, "required": ["empresa"]}},
            {"name": "spec_analyst", "description": "Analisa documentos de engenharia (plantas, memoriais, normas NBR) e extrai requisitos tecnicos.", "inputSchema": {"type": "object", "properties": {"documento": {"type": "string"}, "norma": {"type": "string"}}, "required": ["documento"]}},
            {"name": "bim_coordinator", "description": "Coordena modelos BIM, detecta conflitos e gera relatorio de compatibilizacao IFC.", "inputSchema": {"type": "object", "properties": {"projeto": {"type": "string"}, "disciplinas": {"type": "array", "items": {"type": "string"}}}, "required": ["projeto"]}},
            {"name": "dynamics_sales", "description": "Automatiza vendas no Dynamics 365: qualifica leads, preve receita e gerencia pipeline.", "inputSchema": {"type": "object", "properties": {"lead_id": {"type": "string"}, "acao": {"type": "string"}}, "required": ["lead_id", "acao"]}},
            {"name": "compliance_score", "description": "Calcula score de conformidade regulatoria da empresa com base em NR-1, LGPD e ESG.", "inputSchema": {"type": "object", "properties": {"empresa": {"type": "string"}, "frameworks": {"type": "array", "items": {"type": "string"}}}, "required": ["empresa"]}},
            {"name": "canal_denuncias", "description": "Gerencia canal de denuncias anonimo conforme Lei Anticorrupcao e ISO 37001.", "inputSchema": {"type": "object", "properties": {"descricao": {"type": "string"}, "categoria": {"type": "string"}}, "required": ["descricao"]}},
            {"name": "inventario_carbono", "description": "Calcula inventario de emissoes de carbono (Escopos 1, 2 e 3) conforme GHG Protocol.", "inputSchema": {"type": "object", "properties": {"empresa": {"type": "string"}, "escopos": {"type": "array", "items": {"type": "integer"}}}, "required": ["empresa"]}},
            {"name": "igualdade_salarial", "description": "Analisa equidade salarial conforme Lei 14.611/2023 e gera relatorio para MTE.", "inputSchema": {"type": "object", "properties": {"empresa": {"type": "string"}, "cnpj": {"type": "string"}}, "required": ["empresa"]}},
        ]
    }


@app.get("/mcp/toolspec.json")
async def mcp_toolspec_get():
    return await _mcp_toolspec_data()


@app.post("/mcp/toolspec.json")
async def mcp_toolspec_post():
    return await _mcp_toolspec_data()




@app.get("/mcp/{server_id}/manifest")
async def mcp_server_manifest(server_id: str):
    server = MCP_SERVERS.get(server_id)
    if not server:
        raise HTTPException(status_code=404, detail=f"MCP server '{server_id}' not found")
    return {"id": server_id, "name": f"AION {server_id.title()} MCP", "description": f"MCP server for {server_id} agents", "tools": [{"name": t} for t in server["tools"]]}


@app.get("/api/v1/agents")
async def v1_list_agents():
    return {"agents": list(orchestrator.agents.keys()), "total": len(orchestrator.agents)}


@app.get("/api/v1/subscriptions/plans")
async def v1_list_plans():
    return {"plans": [{"id": p["id"], "name": p["name"], "price": p["price"], "agents": p["agents"]} for p in PLANS]}


@app.get("/api/v1/subscriptions/plans/{plan_id}")
async def v1_get_plan(plan_id: str):
    plan = get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"plan": plan}

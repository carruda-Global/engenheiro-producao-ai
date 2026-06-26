from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.mcp.base_server import MCPServer, MCPTool

erp_app = FastAPI(title="Ecosystem ERP MCP Server", version="3.0.0")

mcp = MCPServer(
    server_id="ecosystem-erp",
    name="Ecosystem ERP MCP",
    description="Agentes ERP — Dynamics 365, Salesforce Agentforce, Oracle Fusion, SAP"
)

def _dynamics_sales(pipeline_data: str = "") -> dict:
    return {"tool": "dynamics_sales", "status": "simulated", "message": "Pipeline D365 analisado", "deals_at_risk": 3, "forecast_brl": 850000.0}

def _dynamics_finance(period: str = "current_month") -> dict:
    return {"tool": "dynamics_finance", "status": "simulated", "message": "Fluxo de caixa D365 analisado", "receivables_brl": 320000.0, "payables_brl": 280000.0}

def _dynamics_hr(payroll_data: str = "") -> dict:
    return {"tool": "dynamics_hr", "status": "simulated", "message": "Folha D365 analisada conforme Lei 14.611/2023", "equity_gap_pct": 12.3}

def _agentforce_sdr(lead_data: str = "") -> dict:
    return {"tool": "agentforce_sdr", "status": "simulated", "message": "Lead qualificado via Sales Cloud", "score": 78, "next_action": "Agendar demo"}

def _agentforce_contracts(contract_text: str = "") -> dict:
    return {"tool": "agentforce_contracts", "status": "simulated", "message": "Contrato revisado via Agentforce", "risks_found": 2, "compliance_issues": ["LGPD: clausula padrao ANPD ausente"]}

def _oracle_erp_compliance(period: str = "") -> dict:
    return {"tool": "oracle_erp_compliance", "status": "simulated", "message": "Auditoria fiscal Oracle ERP concluida", "compliance_status": "parcial", "total_risk_brl": 45000.0}

def _oracle_hcm_regulatory(hcm_data: str = "") -> dict:
    return {"tool": "oracle_hcm_regulatory", "status": "simulated", "message": "Conformidade trabalhista Oracle HCM", "overall_compliance_pct": 65.0, "nr1_status": "pendente", "igualdade_status": "conforme"}

def _sap_compliance_bridge(grc_data: str = "") -> dict:
    return {"tool": "sap_compliance_bridge", "status": "simulated", "message": "GRC SAP verificado", "violations": 2, "overall_grc_score_pct": 82.0}

def _sap_cbam_export(export_data: str = "") -> dict:
    return {"tool": "sap_cbam_export", "status": "simulated", "message": "CBAM calculado via SAP GTS", "products": 2, "total_cbam_cost_eur": 225000.0}

def _powerbi_compliance(tenant_data: str = "") -> dict:
    return {"tool": "powerbi_compliance", "status": "simulated", "message": "Dashboard Power BI gerado", "overall_score_pct": 62.0, "urgent_items": ["Completar mapeamento LGPD"]}

mcp.register_tool(MCPTool(name="dynamics_sales", description="Analisa pipeline Dynamics 365 Sales", handler=_dynamics_sales, parameters={"pipeline_data": {"type": "string"}}))
mcp.register_tool(MCPTool(name="dynamics_finance", description="Analisa fluxo de caixa Dynamics 365 Finance", handler=_dynamics_finance, parameters={"period": {"type": "string"}}))
mcp.register_tool(MCPTool(name="dynamics_hr", description="Analisa equidade salarial Dynamics 365 HR", handler=_dynamics_hr, parameters={"payroll_data": {"type": "string"}}, sensitive=True))
mcp.register_tool(MCPTool(name="agentforce_sdr", description="Qualifica leads no Salesforce Sales Cloud", handler=_agentforce_sdr, parameters={"lead_data": {"type": "string"}}))
mcp.register_tool(MCPTool(name="agentforce_contracts", description="Revisa contratos no Salesforce Agentforce", handler=_agentforce_contracts, parameters={"contract_text": {"type": "string"}}, sensitive=True))
mcp.register_tool(MCPTool(name="oracle_erp_compliance", description="Audita conformidade fiscal Oracle ERP", handler=_oracle_erp_compliance, parameters={"period": {"type": "string"}}))
mcp.register_tool(MCPTool(name="oracle_hcm_regulatory", description="Verifica conformidade trabalhista Oracle HCM", handler=_oracle_hcm_regulatory, parameters={"hcm_data": {"type": "string"}}, sensitive=True))
mcp.register_tool(MCPTool(name="sap_compliance_bridge", description="Verifica GRC e segregação SAP", handler=_sap_compliance_bridge, parameters={"grc_data": {"type": "string"}}))
mcp.register_tool(MCPTool(name="sap_cbam_export", description="Calcula CBAM para exportadores UE via SAP", handler=_sap_cbam_export, parameters={"export_data": {"type": "string"}}))
mcp.register_tool(MCPTool(name="powerbi_compliance", description="Gera dashboard Power BI de compliance", handler=_powerbi_compliance, parameters={"tenant_data": {"type": "string"}}))


class ToolCallRequest(BaseModel):
    tool: str
    params: dict = {}
    tenant_id: str = "default"


@erp_app.get("/health")
async def health():
    return {"status": "healthy", "server": mcp.server_id}


@erp_app.get("/mcp/manifest")
async def manifest():
    return mcp.manifest()


@erp_app.get("/mcp/tools")
async def list_tools():
    return {"tools": mcp.get_tools_list()}


@erp_app.post("/mcp/call")
async def call_tool(req: ToolCallRequest):
    result = await mcp.call_tool(req.tool, req.params, req.tenant_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

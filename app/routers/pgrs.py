import json
import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.config import Settings
from src.orchestrator import Orchestrator
from src.agents import DiagnosticAgent, MonitoringAgent
from src.api.deepseek_client import DeepSeekClient

logger = logging.getLogger(__name__)

router = APIRouter()
settings = Settings()
llm = DeepSeekClient(settings)
orchestrator = Orchestrator(settings)
diagnostic_agent = DiagnosticAgent(settings, llm)
monitoring_agent = MonitoringAgent(settings, llm)


class OrcamentoRequest(BaseModel):
    empresa: str
    cnpj: str = ""
    responsavel: str = ""
    crea: str = ""
    residuos: str
    estimativa: str = ""
    observacoes: str = ""


class PGRSGenerateRequest(BaseModel):
    empresa: str
    cnpj: str = ""
    responsavel: str = ""
    crea: str = ""
    documentos: str = ""
    residuos: str = ""
    activity_description: str = ""


_pgrs_db: dict[str, dict] = {}


@router.post("/orcamento")
async def solicitar_orcamento(req: OrcamentoRequest):
    orcamento_id = f"ORC-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.utcnow().isoformat()

    _pgrs_db[orcamento_id] = {
        "id": orcamento_id,
        "status": "orcamento_solicitado",
        "empresa": req.empresa,
        "cnpj": req.cnpj,
        "created_at": now,
    }

    agent_input = (
        f"EMPRESA: {req.empresa}\n"
        f"CNPJ: {req.cnpj}\n"
        f"RESPONSAVEL: {req.responsavel}\n"
        f"CREA: {req.crea}\n"
        f"RESIDUOS: {req.residuos}\n"
        f"ESTIMATIVA: {req.estimativa}\n"
        f"OBSERVACOES: {req.observacoes}"
    )

    try:
        if "spec_analyst" in orchestrator.agents:
            analysis = orchestrator.agents["spec_analyst"].analyze_document(agent_input)
        else:
            analysis = {"analysis": "Agente SpecAnalyst nao disponivel"}
        waste = diagnostic_agent.classify_waste(agent_input)
        if "compliance" in orchestrator.agents:
            compliance = orchestrator.agents["compliance"].check_compliance(agent_input)
        else:
            compliance = {"compliance_report": "Agente Compliance nao disponivel"}

        _pgrs_db[orcamento_id].update({
            "status": "analise_concluida",
            "spec_analysis": analysis.get("analysis", ""),
            "waste_classification": waste.get("waste_classification", ""),
            "compliance_report": compliance.get("compliance_report", ""),
        })
    except Exception as e:
        logger.error("Erro na analise PGRS: %s", e)
        _pgrs_db[orcamento_id]["status"] = "erro_analise"

    return {
        "orcamento_id": orcamento_id,
        "status": _pgrs_db[orcamento_id]["status"],
        "message": "Orcamento recebido! Recebera uma proposta em ate 24h.",
        "empresa": req.empresa,
    }


@router.post("/gerar")
async def gerar_pgrs(req: PGRSGenerateRequest):
    doc_id = f"PGRS-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.utcnow().isoformat()

    full_input = (
        f"EMPRESA: {req.empresa}\n"
        f"CNPJ: {req.cnpj}\n"
        f"RESPONSAVEL: {req.responsavel}\n"
        f"CREA: {req.crea}\n"
        f"DOCUMENTOS: {req.documentos}\n"
        f"RESIDUOS: {req.residuos}\n"
        f"ATIVIDADE: {req.activity_description}"
    )

    results = {}
    agent_chain = [
        ("spec_analyst", "document_analysis"),
        ("diagnostic", "waste_classification"),
        ("compliance", "pgrs_base"),
    ]

    for agent_id, result_key in agent_chain:
        try:
            if agent_id == "diagnostic":
                results[result_key] = diagnostic_agent.classify_waste(full_input)
            elif agent_id == "spec_analyst" and agent_id in orchestrator.agents:
                results[result_key] = orchestrator.agents[agent_id].analyze_document(full_input)
            elif agent_id == "compliance" and agent_id in orchestrator.agents:
                results[result_key] = orchestrator.agents[agent_id].check_compliance(full_input)
        except Exception as e:
            logger.error("Erro no agente %s: %s", agent_id, e)
            results[result_key] = {"error": str(e)}

    monitoring = monitoring_agent.schedule_renewal(
        client_id=doc_id,
        client_name=req.empresa,
        issue_date=now,
    )

    pgrs_data = {
        "id": doc_id,
        "empresa": req.empresa,
        "cnpj": req.cnpj,
        "responsavel": req.responsavel,
        "crea": req.crea,
        "created_at": now,
        "status": "aguardando_revisao",
        "results": results,
        "monitoring": monitoring,
    }
    _pgrs_db[doc_id] = pgrs_data

    return {
        "id": doc_id,
        "status": "aguardando_revisao",
        "message": "PGRS gerado! Aguardando revisao do engenheiro responsavel e emissaoda ART.",
        "empresa": req.empresa,
        "crea": req.crea,
        "proximo_passo": "Revisar o documento em /api/v1/pgrs/revisar/" + doc_id,
    }


@router.get("/revisar/{doc_id}")
async def revisar_pgrs(doc_id: str):
    doc = _pgrs_db.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento PGRS nao encontrado")
    return {
        "documento": doc,
        "acoes": [
            {"label": "Aprovar e emitir ART", "url": f"/api/v1/pgrs/aprovar/{doc_id}"},
            {"label": "Solicitar correcoes", "url": f"/api/v1/pgrs/corrigir/{doc_id}"},
        ],
    }


@router.post("/aprovar/{doc_id}")
async def aprovar_pgrs(doc_id: str):
    doc = _pgrs_db.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento PGRS nao encontrado")

    doc["status"] = "aprovado"
    doc["approved_at"] = datetime.utcnow().isoformat()
    art_number = f"ART-{uuid.uuid4().hex[:12].upper()}"

    _pgrs_db[doc_id] = doc

    return {
        "id": doc_id,
        "status": "aprovado",
        "art": art_number,
        "message": "PGRS aprovado e ART emitida com sucesso!",
        "observability": "/api/v1/cross-selling/observability",
    }


@router.get("/status/{doc_id}")
async def status_pgrs(doc_id: str):
    doc = _pgrs_db.get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento PGRS nao encontrado")
    return {
        "id": doc_id,
        "status": doc.get("status"),
        "empresa": doc.get("empresa"),
        "created_at": doc.get("created_at"),
        "monitoring": doc.get("monitoring"),
    }

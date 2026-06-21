from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.config import Settings
from src.api.deepseek_client import DeepSeekClient
from src.orchestrator import Orchestrator

router = APIRouter()
settings = Settings()
llm = DeepSeekClient(settings)
orchestrator = Orchestrator(settings)


class AnalyzeDocumentRequest(BaseModel):
    document: str


class ProcessOrderRequest(BaseModel):
    materials: list[dict]


class CheckStockRequest(BaseModel):
    items: list[dict]


class TrackShipmentRequest(BaseModel):
    shipment: dict


class FieldInstructionsRequest(BaseModel):
    specs: str


class WorkflowRequest(BaseModel):
    document: str


@router.post("/spec-analyst/analyze")
async def analyze_document(req: AnalyzeDocumentRequest):
    if "spec_analyst" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Spec Analyst nao disponivel")
    return orchestrator.agents["spec_analyst"].analyze_document(req.document)


@router.post("/procurement/process-order")
async def process_order(req: ProcessOrderRequest):
    if "procurement" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Procurement nao disponivel")
    return orchestrator.agents["procurement"].process_order(req.materials)


@router.post("/inventory/check-stock")
async def check_stock(req: CheckStockRequest):
    if "inventory" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Inventory nao disponivel")
    return orchestrator.agents["inventory"].check_stock(req.items)


@router.post("/logistics/track-shipment")
async def track_shipment(req: TrackShipmentRequest):
    if "logistics" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Logistics nao disponivel")
    return orchestrator.agents["logistics"].track_shipment(req.shipment)


@router.post("/field-execution/instructions")
async def field_instructions(req: FieldInstructionsRequest):
    if "field_execution" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Field Execution nao disponivel")
    return orchestrator.agents["field_execution"].generate_field_instructions(req.specs)


@router.post("/workflow")
async def run_workflow(req: WorkflowRequest):
    results = orchestrator.process_workflow({"document": req.document})
    return {"results": results}


@router.get("")
async def list_agents():
    return {
        "agents": list(orchestrator.agents.keys()),
        "total": len(orchestrator.agents),
    }

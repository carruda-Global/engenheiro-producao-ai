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


class BIMElementRequest(BaseModel):
    description: str


class RequirementsRequest(BaseModel):
    requirements: str


class QuestionRequest(BaseModel):
    question: str
    context: str = ""


class TaskDataRequest(BaseModel):
    task_data: str


class PhotoDescriptionRequest(BaseModel):
    photo_description: str


class ProjectDataRequest(BaseModel):
    project_data: str


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


@router.post("/bim-coordinator/generate-bim-element")
async def generate_bim_element(req: BIMElementRequest):
    if "bim_coordinator" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente BIM Coordinator nao disponivel")
    return orchestrator.agents["bim_coordinator"].generate_bim_element(req.description)


@router.post("/requirements-analyst/analyze-requirements")
async def analyze_requirements(req: RequirementsRequest):
    if "requirements_analyst" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Requirements Analyst nao disponivel")
    return orchestrator.agents["requirements_analyst"].analyze_requirements(req.requirements)


@router.post("/engineering-assistant/answer-question")
async def answer_question(req: QuestionRequest):
    if "engineering_assistant" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Engineering Assistant nao disponivel")
    return orchestrator.agents["engineering_assistant"].answer_question(req.question, req.context)


@router.post("/work-synopsis/generate-synopsis")
async def generate_synopsis(req: TaskDataRequest):
    if "work_synopsis" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Work Synopsis nao disponivel")
    return orchestrator.agents["work_synopsis"].generate_synopsis(req.task_data)


@router.post("/photo-intelligence/analyze-photo")
async def analyze_photo(req: PhotoDescriptionRequest):
    if "photo_intelligence" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Photo Intelligence nao disponivel")
    return orchestrator.agents["photo_intelligence"].analyze_photo(req.photo_description)


@router.post("/rfi-creation/create-rfi")
async def create_rfi(req: QuestionRequest):
    if "rfi_creation" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente RFI Creation nao disponivel")
    return orchestrator.agents["rfi_creation"].create_rfi(req.question, req.context)


@router.post("/compliance/check-compliance")
async def check_compliance(req: ProjectDataRequest):
    if "compliance" not in orchestrator.agents:
        raise HTTPException(status_code=404, detail="Agente Compliance nao disponivel")
    return orchestrator.agents["compliance"].check_compliance(req.project_data)


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

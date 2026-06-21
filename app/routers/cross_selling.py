from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.config import Settings
from src.orchestrator import Orchestrator
from src.cross_selling import (
    get_next_upgrade,
    get_upsell_plans,
    estimate_monthly_savings,
    get_agent_name,
    AGENT_CHAIN,
)

router = APIRouter()
settings = Settings()
orchestrator = Orchestrator(settings)


@router.get("/chain")
async def get_agent_chain():
    return {
        "chain": [{"id": a, "name": get_agent_name(a)} for a in AGENT_CHAIN],
        "total": len(AGENT_CHAIN),
    }


@router.get("/upgrade/{current_plan_id}")
async def suggest_upgrade(current_plan_id: str):
    next_plan = get_next_upgrade(current_plan_id)
    if not next_plan:
        return {
            "current_plan": current_plan_id,
            "message": "Voce ja esta no plano maximo disponivel",
            "upgrade_available": False,
        }
    return {
        "current_plan": current_plan_id,
        "upgrade_available": True,
        "next_plan": {
            "id": next_plan["id"],
            "name": next_plan["name"],
            "price": next_plan["price"],
            "price_monthly": next_plan["price"] / 100,
            "agents": [get_agent_name(a) for a in next_plan["agents"]],
            "new_agents": get_agent_name,
        },
        "savings": {
            "monthly": estimate_monthly_savings(current_plan_id, next_plan["id"]),
        },
    }


@router.get("/upsell/{current_plan_id}")
async def suggest_upsells(current_plan_id: str):
    plans = get_upsell_plans(current_plan_id)
    return {
        "current_plan": current_plan_id,
        "suggestions": [
            {
                "id": p["id"],
                "name": p["name"],
                "price": p["price"],
                "price_monthly": p["price"] / 100,
                "features": p["features"],
            }
            for p in plans
        ],
        "total_suggestions": len(plans),
    }


@router.get("/observability")
async def governance_summary():
    from src.governance import TrustScorer

    scorer = TrustScorer()
    return scorer.get_summary()

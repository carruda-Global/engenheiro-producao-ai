PLANS = [
    {"id": "starter", "name": "AEC Starter", "price_brl": 997, "price_usd": 249, "agents": ["#1"]},
    {"id": "professional", "name": "AEC Professional", "price_brl": 2391, "price_usd": 599, "agents": ["#1", "#2", "#3"]},
    {"id": "enterprise", "name": "AEC Enterprise", "price_brl": 4685, "price_usd": 1199, "agents": ["#1", "#2", "#3", "#4", "#5"]},
    {"id": "regulatory_starter", "name": "Compliance Essencial", "price_brl": 590, "price_usd": 149, "agents": ["#13", "#15"]},
    {"id": "regulatory_pro", "name": "Regulatory Pro", "price_brl": 1490, "price_usd": 379, "agents": ["#13", "#15", "#19", "#20", "#21"]},
    {"id": "esg_carbono", "name": "ESG + Carbono", "price_brl": 2490, "price_usd": 629, "agents": ["#16", "#17", "#18"]},
    {"id": "microsoft_pack", "name": "Microsoft Pack", "price_brl": 4482, "price_usd": 1129, "agents": ["#22", "#23", "#24", "#25", "#26", "#27"]},
    {"id": "dynamics_pack", "name": "Dynamics Pack", "price_brl": 3990, "price_usd": 999, "agents": ["#31", "#32", "#33", "#34", "#35", "#36"]},
    {"id": "agentforce_pack", "name": "Agentforce Pack", "price_brl": 3690, "price_usd": 929, "agents": ["#37", "#38", "#39", "#40", "#41"]},
    {"id": "oracle_pack", "name": "Oracle Pack", "price_brl": 3990, "price_usd": 999, "agents": ["#42", "#43", "#44", "#45"]},
    {"id": "sap_pack", "name": "SAP Pack", "price_brl": 4290, "price_usd": 1079, "agents": ["#46", "#47", "#48"]},
    {"id": "erp_full_bridge", "name": "ERP Full Bridge", "price_brl": 12990, "price_usd": 3299, "agents": ["#31", "#32", "#33", "#34", "#35", "#36", "#37", "#38", "#39", "#40", "#41", "#42", "#43", "#44", "#45", "#46", "#47", "#48"]},
    {"id": "tech_starter", "name": "Tech Starter", "price_brl": 1997, "price_usd": 499, "agents": ["#57"]},
    {"id": "tech_professional", "name": "Tech Professional", "price_brl": 3497, "price_usd": 899, "agents": ["#57", "#58", "#59"]},
    {"id": "tech_enterprise", "name": "Tech Enterprise", "price_brl": 5997, "price_usd": 1499, "agents": ["#57", "#58", "#59", "#49", "#50"]},
    {"id": "cross_sell_pack", "name": "Cross-Sell Pack", "price_brl": 297, "price_usd": 79, "agents": ["N1", "N2", "N3"]},
    {"id": "full_suite", "name": "Full Suite", "price_brl": 19997, "price_usd": 4999, "agents": ["all_71"]},
]


def get_plan(plan_id: str) -> dict:
    return get_plan_by_id(plan_id)


def get_plan_by_id(plan_id: str) -> dict:
    for p in PLANS:
        if p["id"] == plan_id:
            return p
    return {}


def get_plan_by_price(price_brl: float) -> dict:
    for p in PLANS:
        if p["price_brl"] == price_brl:
            return p
    return {}

"""
Gera ofertas SaaS para o Microsoft Azure Marketplace (12 agentes).

Uso:
    python scripts/generate_microsoft_marketplace.py

Gera:
    - offers/ecosystem-aec-offer.json (listing completo)
    - Instrucoes para publicacao no Partner Center
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

PLANS = [
    {
        "id": "starter",
        "name": "Starter - Spec Analyst",
        "description": "1 agente de IA para analise de especificacoes tecnicas",
        "monthly_price_usd": 199.00,
        "agents": ["Spec Analyst"],
    },
    {
        "id": "professional",
        "name": "Professional - 3 Agentes",
        "description": "Spec Analyst + Procurement + Inventory",
        "monthly_price_usd": 399.00,
        "agents": ["Spec Analyst", "Procurement", "Inventory"],
    },
    {
        "id": "enterprise",
        "name": "Enterprise - 5 Agentes",
        "description": "5 agentes do nucleo AEC: analise, compras, estoque, logistica, campo",
        "monthly_price_usd": 799.00,
        "agents": ["Spec Analyst", "Procurement", "Inventory", "Logistics", "Field Execution"],
    },
    {
        "id": "full_suite",
        "name": "Full Suite - 12 Agentes",
        "description": "Ecossistema completo de 12 agentes de IA para AEC",
        "monthly_price_usd": 1599.00,
        "agents": [
            "Spec Analyst", "Procurement", "Inventory", "Logistics",
            "Field Execution", "BIM Coordinator", "Requirements Analyst",
            "Engineering Assistant", "Work Synopsis", "Photo Intelligence",
            "RFI Creation", "Compliance Agent",
        ],
    },
    {
        "id": "compliance_pack",
        "name": "Compliance Pack - PGRS/PGRSS",
        "description": "Photo Intelligence + RFI Creation + Compliance Agent",
        "monthly_price_usd": 399.00,
        "agents": ["Photo Intelligence", "RFI Creation", "Compliance Agent"],
    },
]

OFFER = {
    "$schema": "https://schema.mp.azure.com/schema/2024-03-01/offer.json",
    "id": "ecosystem_aec",
    "name": "EcoSystem AEC",
    "alias": "ecosystem-aec",
    "description": "12 Agentes de IA Integrados para Arquitetura, Engenharia e Construcao",
    "publisher": {
        "id": "projato_engenharia",
        "name": "Projato Engenharia",
    },
    "kind": "SaaS",
    "categories": ["AI + Machine Learning", "Developer Tools"],
    "industries": ["Engineering and Construction", "Architecture"],
    "plans": [],
}

for plan in PLANS:
    offer_plan = {
        "id": plan["id"],
        "name": plan["name"],
        "description": plan["description"],
        "pricing": {
            "type": "recurring",
            "interval": "month",
            "price_usd": plan["monthly_price_usd"],
            "currency": "USD",
        },
        "hidden": False,
        "components": [
            {
                "name": plan["name"],
                "type": "SaaS",
                "description": plan["description"],
                "provisioning_url": "https://ecosystem-aec.onrender.com/api/v1/subscriptions/checkout",
                "provisioning_type": "redirect",
            }
        ],
    }
    OFFER["plans"].append(offer_plan)


def main():
    output_dir = Path(__file__).parent.parent / "offers"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "ecosystem-aec-offer.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(OFFER, f, ensure_ascii=False, indent=2)

    print(f"Oferta Microsoft Marketplace gerada: {output_path}")
    print(f"Planos: {len(PLANS)}")
    for p in PLANS:
        print(f"  - {p['name']:30s} | ${p['monthly_price_usd']:.2f}/mes | {len(p['agents'])} agentes")
    print()
    print("Para publicar no Microsoft Partner Center:")
    print("  1. Acesse https://partner.microsoft.com")
    print("  2. Crie uma oferta SaaS")
    print("  3. Importe o arquivo offers/ecosystem-aec-offer.json")
    print("  4. Configure a URL de provisionamento:")
    print("     https://ecosystem-aec.onrender.com/api/v1/subscriptions/checkout")
    print("  5. Publique para certificacao")


if __name__ == "__main__":
    main()

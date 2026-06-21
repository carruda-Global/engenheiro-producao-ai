import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings

OFFER_TEMPLATE = {
    "offer": {
        "id": "engenheiro-producao-ai",
        "title": "Engenheiro de Produção AI - Automação Inteligente para AEC",
        "description": "Sistema multiagente de IA especializado na indústria de Arquitetura, Engenharia e Construção (AEC). Automatiza análise de especificações técnicas, processamento de compras, gestão de estoque, rastreamento logístico e geração de instruções de execução em campo.",
        "publisher": {
            "name": "",
            "website": "",
            "support_email": "",
            "support_url": "",
        },
        "categories": ["AI Apps and Agents", "Machine Learning"],
        "industry": ["Engineering and Construction", "Architecture and Construction"],
        "type": "SaaS",
        "plans": [
            {
                "id": "starter",
                "name": "Starter - Spec Analyst",
                "description": "Acesso ao agente Analisador de Especificações Técnicas",
                "price": 997.00,
                "currency": "BRL",
                "billing": "monthly",
                "agents": ["spec_analyst"],
            },
            {
                "id": "professional",
                "name": "Professional",
                "description": "Agentes de especificações, compras e estoque",
                "price": 1597.00,
                "currency": "BRL",
                "billing": "monthly",
                "agents": ["spec_analyst", "procurement", "inventory"],
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "description": "Agentes de especificações, compras, estoque e logística",
                "price": 2997.00,
                "currency": "BRL",
                "billing": "monthly",
                "agents": ["spec_analyst", "procurement", "inventory", "logistics"],
            },
            {
                "id": "full-suite",
                "name": "Full Suite",
                "description": "Todos os 5 agentes de IA para gestão completa de obras",
                "price": 3500.00,
                "currency": "BRL",
                "billing": "monthly",
                "agents": ["spec_analyst", "procurement", "inventory", "logistics", "field_execution"],
            },
        ],
        "technical_configuration": {
            "authentication": "API Key",
            "api_endpoint": "https://engenheiro-producao-ai.onrender.com/api/v1",
            "sso_enabled": False,
            "cors_support": True,
        },
        "listing": {
            "summary": "Automação com IA para construção civil: análise de specs, compras, estoque, logística e execução em campo.",
            "industries": ["Architecture & Construction", "Engineering"],
            "countries": ["BR"],
            "languages": ["pt-BR"],
            "search_keywords": ["engenharia", "construção civil", "AEC", "IA", "agente IA", "obra", "especificações técnicas"],
        },
    }
}


def generate_offer_json():
    settings = Settings()

    offer = OFFER_TEMPLATE.copy()
    offer["offer"]["publisher"]["name"] = "Projato Engenharia"
    offer["offer"]["publisher"]["support_email"] = "suporte@projato.com.br"
    offer["offer"]["publisher"]["support_url"] = "https://engenheiro-producao-ai.onrender.com"

    output_path = Path(__file__).parent.parent / "config" / "microsoft_marketplace_offer.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(offer, f, indent=2, ensure_ascii=False)

    print(f"Arquivo de oferta gerado: {output_path}")
    print()
    print("Próximos passos manuais no Microsoft Partner Center:")
    print("  1. Acesse https://partner.microsoft.com")
    print("  2. Cadastre-se no Microsoft AI Cloud Partner Program")
    print("  3. Crie uma nova oferta > SaaS")
    print("  4. Use o arquivo gerado como referência para preencher:")
    print("     - Nome e descrição do produto")
    print("     - Categoria: AI Apps and Agents")
    print("     - Planos de precificação (4 tiers)")
    print("     - Configuração técnica (API endpoint)")
    print("  5. Configure Stripe como processador de pagamento integrado")
    print("  6. Envie para revisão e publicação")


if __name__ == "__main__":
    generate_offer_json()

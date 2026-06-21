import stripe
import os
import json
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

products = [
    {"name": "Starter - Spec Analyst", "price": 99700, "agents": ["spec_analyst"]},
    {"name": "Professional", "price": 159700, "agents": ["spec_analyst", "procurement"]},
    {"name": "Enterprise", "price": 299700, "agents": ["spec_analyst", "procurement", "inventory", "logistics"]},
    {"name": "Full Suite", "price": 350000, "agents": ["spec_analyst", "procurement", "inventory", "logistics", "field_execution"]},
]

results = []
for p in products:
    prod = stripe.Product.create(name=p["name"], metadata={"agents": json.dumps(p["agents"])})
    price = stripe.Price.create(
        product=prod.id,
        unit_amount=p["price"],
        currency="brl",
        recurring={"interval": "month"},
    )
    results.append({"product_id": prod.id, "price_id": price.id, "name": p["name"]})
    print(f"{p['name']:30s} | Produto: {prod.id:20s} | Preco: {price.id}")

# Save to config
import yaml
config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

for r in results:
    key = r["name"].lower().replace(" ", "_").replace("-", "_").replace("__", "_")
    if key.startswith("starter"): plan_key = "starter"
    elif key.startswith("professional"): plan_key = "professional"
    elif key.startswith("enterprise"): plan_key = "enterprise"
    elif key.startswith("full"): plan_key = "full_suite"
    else: continue
    config["stripe"]["plans"][plan_key]["price_id"] = r["price_id"]

with open(config_path, "w", encoding="utf-8") as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

print("\nConfiguracao atualizada em config.yaml!")

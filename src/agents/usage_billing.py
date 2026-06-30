import stripe
from fastapi import APIRouter, Request
from src.config import Settings

router = APIRouter(prefix="/api/usage", tags=["usage_billing"])

PRICING_PER_USE = {
    "BR": {"nr1_diagnostico": ("brl", 1990), "lgpd_scan": ("brl", 2990)},
    "US": {"eu_ai_act_check": ("usd", 1999)},
    "MX": {"lfpdppp_check": ("mxn", 49000)},
    "CO": {"ley1581_check": ("cop", 18000000)},
    "AR": {"sdr_diagnostic": ("usd", 990)},
}


class UsageBillingAgent:
    def __init__(self, settings: Settings):
        self.settings = settings

    def create_one_time_charge(self, market: str, agent_id: str, email: str) -> str:
        if market not in PRICING_PER_USE or agent_id not in PRICING_PER_USE[market]:
            return ""
        currency, amount = PRICING_PER_USE[market][agent_id]
        stripe.api_key = self.settings.stripe_secret_key
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": currency,
                    "product_data": {"name": f"Diagnóstico {agent_id}"},
                    "unit_amount": amount,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://global-engenharia.com/ecosystem/sucesso",
            cancel_url="https://global-engenharia.com/ecosystem",
            customer_email=email,
        )
        return session.url


@router.post("/pay-per-use/{market}/{agent_id}")
async def create_usage_payment(market: str, agent_id: str, request: Request):
    data = await request.json()
    agent = UsageBillingAgent(Settings())
    url = agent.create_one_time_charge(market.upper(), agent_id, data.get("email", ""))
    return {"checkout_url": url}

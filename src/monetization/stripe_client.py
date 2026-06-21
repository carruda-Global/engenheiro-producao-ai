import stripe
from src.config import Settings


class StripeClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        stripe.api_key = settings.stripe_secret_key

    def create_checkout_session(
        self,
        plan_id: str,
        success_url: str,
        cancel_url: str,
        customer_email: str | None = None,
    ) -> str | None:
        plan_config = self.settings.plans_config.get(plan_id)
        if not plan_config:
            return None

        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[
                {
                    "price_data": {
                        "currency": "brl",
                        "product_data": {"name": plan_config["name"]},
                        "unit_amount": plan_config["amount_cents"],
                        "recurring": {"interval": "month"},
                    },
                    "quantity": 1,
                }
            ],
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
            subscription_data={
                "trial_period_days": 15,
            },
        )
        return session.url

    def cancel_subscription(self, subscription_id: str) -> bool:
        try:
            stripe.Subscription.delete(subscription_id)
            return True
        except Exception:
            return False

    def get_subscription(self, subscription_id: str) -> dict | None:
        try:
            sub = stripe.Subscription.retrieve(subscription_id)
            return {"id": sub.id, "status": sub.status, "plan": sub.plan}
        except Exception:
            return None

    def handle_webhook(self, payload: bytes, sig_header: str) -> dict:
        endpoint_secret = self.settings.stripe_secret_key
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        return {"type": event.type, "data": event.data.object}

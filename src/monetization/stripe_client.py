import stripe
from src.config import Settings


class StripeClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._configure_api()

    def _configure_api(self):
        key = self.settings.stripe_secret_key
        if not key or key.startswith("sk_live_51Tkp"):
            import warnings
            warnings.warn(
                "Stripe live key seems exposed or invalid. Set STRIPE_SECRET_KEY via env var only."
            )
        stripe.api_key = key

    def _get_webhook_secret(self) -> str:
        env = self.settings.app_env
        secret = getattr(self.settings, f"stripe_webhook_secret_{env}", None)
        if not secret:
            secret = self.settings.stripe_webhook_secret
        return secret

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

        price_id = plan_config.get("price_id")
        if price_id:
            line_items = [{"price": price_id, "quantity": 1}]
        else:
            line_items = [{
                "price_data": {
                    "currency": "brl",
                    "product_data": {"name": plan_config["name"]},
                    "unit_amount": plan_config["amount_cents"],
                    "recurring": {"interval": "month"},
                },
                "quantity": 1,
            }]

        metadata = {"plan_id": plan_id}

        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=line_items,
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
            subscription_data={"trial_period_days": 15, "metadata": metadata},
            metadata=metadata,
        )
        return session.url

    def create_upgrade_session(
        self,
        subscription_id: str,
        new_plan_id: str,
        success_url: str,
        cancel_url: str,
    ) -> str | None:
        plan_config = self.settings.plans_config.get(new_plan_id)
        if not plan_config:
            return None

        price_id = plan_config.get("price_id")
        if not price_id:
            return None

        try:
            sub = stripe.Subscription.retrieve(subscription_id)
            current_item = sub["items"]["data"][0]["id"]

            session = stripe.checkout.Session.create(
                mode="setup",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "action": "upgrade",
                    "subscription_id": subscription_id,
                    "new_plan_id": new_plan_id,
                    "new_price_id": price_id,
                    "subscription_item_id": current_item,
                },
            )
            return session.url
        except Exception:
            return None

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
        endpoint_secret = self._get_webhook_secret()
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        return {"type": event.type, "data": event.data.object}

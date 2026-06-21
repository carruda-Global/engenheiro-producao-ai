import logging
from typing import Any

import google.auth
from google.cloud import marketplace as google_marketplace

from src.config import Settings

logger = logging.getLogger(__name__)


class GoogleCloudMarketplaceClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.product_id = settings.google_product_id
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                credentials, project = google.auth.default()
                self._client = google_marketplace.MarketplaceClient(
                    credentials=credentials
                )
            except Exception as e:
                logger.warning("Erro ao criar Google Marketplace client: %s", e)
        return self._client

    def resolve_ entitlements(self, customer_id: str) -> dict[str, Any] | None:
        client = self._get_client()
        if not client:
            return None
        try:
            request = google_marketplace.GetEntitlementRequest(
                name=f"providers/{self.product_id}/entitlements/{customer_id}"
            )
            response = client.get_entitlement(request=request)
            return {
                "customer_id": customer_id,
                "product_id": self.product_id,
                "state": response.state.name,
                "plan": response.plan_name,
            }
        except Exception as e:
            logger.error("Erro Google entitlements: %s", e)
            return None

    def is_subscription_active(self, customer_id: str) -> bool:
        result = self.resolve_entitlements(customer_id)
        return result is not None and result.get("state") == "ACTIVE"

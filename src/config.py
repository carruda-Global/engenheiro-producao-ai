import os
import re
from pathlib import Path
from dotenv import load_dotenv
import yaml

load_dotenv()


def _resolve_env(value):
    if isinstance(value, str):
        def _replace(match):
            var = match.group(1)
            return os.getenv(var, match.group(0))
        return re.sub(r"\$\{(\w+)\}", _replace, value)
    return value


def _resolve_env_recursive(obj):
    if isinstance(obj, dict):
        return {k: _resolve_env_recursive(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_resolve_env_recursive(v) for v in obj]
    elif isinstance(obj, str):
        return _resolve_env(obj)
    return obj


def load_config(config_path: str | None = None) -> dict:
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config.yaml"

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    config = _resolve_env_recursive(config)
    return config


class Settings:
    def __init__(self, config_path: str | None = None):
        self.config = load_config(config_path)

        self.deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
        self.deepseek_model: str = self.config["deepseek"]["model"]
        self.deepseek_max_tokens: int = self.config["deepseek"]["max_tokens"]
        self.deepseek_temperature: float = self.config["deepseek"]["temperature"]
        self.deepseek_api_base: str = self.config["deepseek"]["api_base"]
        self.deepseek_timeout: int = self.config["deepseek"]["timeout"]

        self.stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
        self.stripe_publishable_key: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
        self.stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")

        self.supabase_url: str = os.getenv("SUPABASE_URL", "")
        self.supabase_api_key: str = os.getenv("SUPABASE_API_KEY", "")

        self.app_env: str = os.getenv("APP_ENV", "development")
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.debug: bool = self.config["app"]["debug"]

        self.aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
        self.aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
        self.aws_region: str = self.config.get("marketplace", {}).get("aws", {}).get("region", "us-east-1")
        self.aws_product_code: str = self.config.get("marketplace", {}).get("aws", {}).get("product_code", "")
        self.aws_sns_topic_arn: str = self.config.get("marketplace", {}).get("aws", {}).get("sns_topic_arn", "")
        self.aws_subscribe_redirect_url: str = os.getenv("AWS_SUBSCRIBE_REDIRECT_URL", "")

        self.oci_config_file: str = os.getenv("OCI_CONFIG_FILE", "~/.oci/config")
        self.oci_profile: str = os.getenv("OCI_PROFILE", "DEFAULT")
        self.oci_use_instance_principal: bool = os.getenv("OCI_USE_INSTANCE_PRINCIPAL", "").lower() == "true"
        self.oci_use_resource_principal: bool = os.getenv("OCI_USE_RESOURCE_PRINCIPAL", "").lower() == "true"
        oracle_config = self.config.get("marketplace", {}).get("oracle", {})
        self.oracle_product_id: str = oracle_config.get("product_id", "")
        self.oracle_seller_id: str = oracle_config.get("seller_id", "")
        self.oracle_enabled: bool = oracle_config.get("enabled", False)

        microsoft_config = self.config.get("marketplace", {}).get("microsoft", {})
        self.microsoft_tenant_id: str = microsoft_config.get("tenant_id", os.getenv("AZURE_TENANT_ID", ""))
        self.microsoft_client_id: str = microsoft_config.get("client_id", os.getenv("AZURE_CLIENT_ID", ""))
        self.microsoft_client_secret: str = microsoft_config.get("client_secret", os.getenv("AZURE_CLIENT_SECRET", ""))
        self.microsoft_fulfillment_api_version: str = microsoft_config.get("fulfillment_api_version", "2018-08-31")
        self.microsoft_enabled: bool = microsoft_config.get("enabled", False)

        self.agents_config: dict = self.config["agents"]
        self.plans_config: dict = self.config["stripe"]["plans"]
        self.cross_selling_config: dict = self.config["cross_selling"]

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.deepseek_api_key:
            errors.append("DEEPSEEK_API_KEY nao configurada")
        return errors

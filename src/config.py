import os
from pathlib import Path
from dotenv import load_dotenv
import yaml

load_dotenv()


def load_config(config_path: str | None = None) -> dict:
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config.yaml"

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

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

        self.agents_config: dict = self.config["agents"]
        self.plans_config: dict = self.config["stripe"]["plans"]
        self.cross_selling_config: dict = self.config["cross_selling"]

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.deepseek_api_key:
            errors.append("DEEPSEEK_API_KEY nao configurada")
        return errors

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_active_subscriptions: dict[str, dict] = {}
_supabase = None


def _init_supabase():
    global _supabase
    if _supabase is not None:
        return _supabase
    try:
        from supabase import create_client
        from src.config import get_settings
        s = get_settings()
        if s.supabase_url and s.supabase_api_key:
            _supabase = create_client(s.supabase_url, s.supabase_api_key)
            _supabase.table("subscriptions").select("id").limit(1).execute()
            logger.info("Supabase conectado para subscriptions")
        else:
            logger.warning("Supabase nao configurado, usando memoria")
    except Exception as e:
        logger.warning("Supabase indisponivel para subscriptions: %s. Usando memoria.", e)
        _supabase = False
    return _supabase


def activate_subscription(
    source: str,
    external_id: str,
    customer_id: str,
    plan_id: str,
    customer_email: str = "",
    customer_name: str = "",
) -> dict:
    sub_id = f"{source}_{external_id}"
    now = datetime.now(timezone.utc).isoformat()

    record = {
        "subscription_id": sub_id,
        "source": source,
        "external_id": external_id,
        "customer_id": customer_id,
        "customer_email": customer_email,
        "customer_name": customer_name,
        "plan_id": plan_id,
        "status": "active",
        "activated_at": now,
    }

    _active_subscriptions[sub_id] = record

    db = _init_supabase()
    if db:
        try:
            db.table("subscriptions").upsert({
                "id": sub_id,
                "source": source,
                "external_id": external_id,
                "customer_id": customer_id,
                "customer_email": customer_email,
                "customer_name": customer_name,
                "plan_id": plan_id,
                "status": "active",
                "activated_at": now,
            }, on_conflict="id").execute()
        except Exception as e:
            logger.warning("Falha ao salvar subscription no Supabase: %s", e)

    logger.info("Assinatura ativada: source=%s sub=%s customer=%s plan=%s", source, sub_id, customer_id, plan_id)
    return record


def deactivate_subscription(source: str, external_id: str) -> bool:
    sub_id = f"{source}_{external_id}"
    sub = _active_subscriptions.get(sub_id)
    if sub:
        sub["status"] = "cancelled"
        sub["cancelled_at"] = datetime.now(timezone.utc).isoformat()

    db = _init_supabase()
    if db:
        try:
            db.table("subscriptions").update({
                "status": "cancelled",
                "cancelled_at": datetime.now(timezone.utc).isoformat(),
            }).eq("id", sub_id).execute()
        except Exception as e:
            logger.warning("Falha ao atualizar subscription no Supabase: %s", e)

    logger.info("Assinatura cancelada: %s", sub_id)
    return True


def get_subscription(source: str, external_id: str) -> dict | None:
    return _active_subscriptions.get(f"{source}_{external_id}")


def list_active_subscriptions() -> list[dict]:
    return [s for s in _active_subscriptions.values() if s["status"] == "active"]


def get_subscription_by_id(subscription_id: str) -> dict | None:
    return _active_subscriptions.get(subscription_id)


def update_subscription_plan(source: str, external_id: str, new_plan_id: str) -> dict | None:
    sub = get_subscription(source, external_id)
    if sub:
        sub["plan_id"] = new_plan_id
        db = _init_supabase()
        if db:
            try:
                db.table("subscriptions").update({"plan_id": new_plan_id}).eq("id", f"{source}_{external_id}").execute()
            except Exception as e:
                logger.warning("Falha ao atualizar plano no Supabase: %s", e)
        logger.info("Plano atualizado: source=%s sub=%s new_plan=%s", source, f"{source}_{external_id}", new_plan_id)
    return sub

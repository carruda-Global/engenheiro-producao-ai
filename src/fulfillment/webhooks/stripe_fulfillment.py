import logging, json, os
from fastapi import APIRouter, Request, HTTPException
import stripe
from src.monetization.stripe_client import StripeClient
from src.database.supabase_client import SupabaseClient
from src.config import Settings
from src.fulfillment.provisioning.activate_tenant import TenantActivator

try:
    from src.fulfillment.email.sender import EmailSender
    email = EmailSender()
except ImportError:
    email = None

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhook", tags=["fulfillment"])
settings = Settings()
db = SupabaseClient(settings)
activator = TenantActivator(db)

PRICE_TO_PLAN = {
    "price_compliance_essencial": "compliance_essencial",
    "price_regulatory_pro": "regulatory_pro",
    "price_esg_carbono": "esg_carbono",
    "price_tributario": "tributario_cbs_ibs",
    "price_microsoft_pack": "microsoft_pack",
    "price_full_suite": "full_suite",
    "price_micro_starter": "micro_starter",
    "price_micro_rh": "micro_rh",
    "price_micro_dev": "micro_dev",
    "price_micro_sales": "micro_sales",
    "price_micro_full": "micro_full",
    "price_tech_starter": "tech_starter",
    "price_tech_professional": "tech_professional",
    "price_tech_enterprise": "tech_enterprise",
    "price_starter": "starter",
    "price_professional": "professional",
    "price_enterprise": "enterprise",
}


@router.post("/stripe/fulfillment")
async def stripe_fulfillment_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    fulfillment_secret = os.getenv("STRIPE_FULFILLMENT_SECRET", stripe.webhook_secret)
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, fulfillment_secret)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event.type
    data = event.data.object

    if event_type == "checkout.session.completed":
        session = data
        customer_email = session.get("customer_details", {}).get("email", "")
        customer_name = session.get("customer_details", {}).get("name", "Cliente")
        plan_id = session.get("metadata", {}).get("plan_id", "")

        if not plan_id:
            line_items = getattr(session, "line_items", None)
            if line_items and line_items.data:
                price_id = line_items.data[0].get("price", "")
                plan_id = PRICE_TO_PLAN.get(price_id, "")
                if not plan_id:
                    plan_id = line_items.data[0].get("price", {}).get("product", {}).get("metadata", {}).get("plan_id", "")

        if not plan_id:
            logger.error(f"Plan ID nao encontrado na sessao {session.id}")
            return {"status": "error", "detail": "plan_id not found"}

        try:
            tenant = activator.activate(customer_email, customer_name, plan_id, session.get("metadata", {}))
            logger.info(f"Entrega automatica concluida: {tenant['id']}")

            subject = f"Bem-vindo ao AION 7.0 - {tenant['plan_name']}"
            html = _montar_email_boas_vindas(tenant)
            if email:
                email.send(customer_email, subject, html)
            else:
                logger.info(f"Email nao enviado (sender nao configurado): {customer_email}")

            return {"status": "delivered", "tenant_id": tenant["id"], "plan": tenant["plan_name"]}
        except Exception as e:
            logger.exception(f"Falha na entrega: {e}")
            return {"status": "error", "detail": str(e)}

    return {"status": "ignored", "event": event_type}


def _montar_email_boas_vindas(tenant: dict) -> str:
    portal_url = os.getenv("PORTAL_URL", "https://global-engenharia.com/ecosystem")
    agentes_html = "".join(f"<li>{a}</li>" for a in tenant.get("agents", []))

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f4f4f5">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:24px">
<table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.08)">
<tr><td style="padding:32px 40px 16px;background:linear-gradient(135deg,#2563eb,#1e40af);text-align:center">
<h1 style="color:#fff;margin:0;font-size:24px">AION 7.0</h1>
<p style="color:rgba(255,255,255,.85);font-size:14px;margin:4px 0 0">Agents Intelligence Orchestration Network</p>
</td></tr>
<tr><td style="padding:32px 40px;font-size:15px;line-height:1.6;color:#1e293b">
<h2 style="margin:0 0 16px;font-size:20px;color:#0f172a">Bem-vindo, {tenant.get('name', 'Cliente')}!</h2>
<p>Sua assinatura do <strong>{tenant['plan_name']}</strong> foi ativada com sucesso.</p>
<p><strong>Agentes liberados:</strong></p>
<ul>{agentes_html}</ul>
<table style="width:100%;background:#f8fafc;border-radius:8px;padding:16px;margin:16px 0">
<tr><td style="font-size:13px;color:#64748b;padding:4px 0"><strong>Tenant ID:</strong> {tenant['id']}</td></tr>
<tr><td style="font-size:13px;color:#64748b;padding:4px 0"><strong>API Key:</strong> <code style="background:#e2e8f0;padding:2px 6px;border-radius:4px;font-size:12px">{tenant['api_key']}</code></td></tr>
</table>
<p style="text-align:center;margin:24px 0">
<a href="{portal_url}" style="display:inline-block;background:#2563eb;color:#fff;padding:12px 32px;border-radius:50px;text-decoration:none;font-weight:700">Acessar Portal</a>
</p>
<h3 style="margin:24px 0 8px;color:#0f172a">Integracao Microsoft</h3>
<p>Para integrar os agentes ao seu ambiente Microsoft 365 (Teams, SharePoint, Planner):</p>
<ol style="margin:0 0 16px;padding-left:20px">
<li>Acesse o portal e copie sua API Key</li>
<li>No Teams, adicione o app "AION Agent"</li>
<li>Cole sua API Key nas configuracoes</li>
<li>Os agentes aparecerao nos canais configurados</li>
</ol>
<p style="background:#fef2f2;padding:12px;border-radius:8px;border-left:4px solid #ef4444;font-size:13px">
Precisa de ajuda? Responda este email ou chame no WhatsApp: <strong>(11) 99479-8464</strong>
</p>
</td></tr>
<tr><td style="padding:24px 40px;background:#f8fafc;font-size:12px;color:#64748b;text-align:center;border-top:1px solid #e2e8f0">
<p style="margin:0">Global Match Engenharia de Producao | CREA-SP 5071200171</p>
<p style="margin:4px 0 0;font-size:11px">© 2026 AION 7.0 - Todos os direitos reservados</p>
</td></tr>
</table></td></tr></table>
</body></html>"""

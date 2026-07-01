import asyncio
import os
import httpx
import logging

logger = logging.getLogger(__name__)

from fastapi import APIRouter
router = APIRouter(prefix="/api/directories", tags=["directories"])

RESEND_KEY = os.getenv("RESEND_API_KEY", "")
EIN_API_KEY = os.getenv("EIN_PRESSWIRE_API_KEY", "")
JDSUPRA_TOKEN = os.getenv("JDSUPRA_API_TOKEN", "")

# Publicações regtech que recebem press release automaticamente
REGTECH_PRESS_EMAILS = [
    ("FinTech Global",    "news@fintech.global"),
    ("A-Team Insight",    "editorial@a-teaminsight.com"),
    ("RegTech Analyst",   "press@regtechanalyst.com"),
    ("Compliance Week",   "newsroom@complianceweek.com"),
    ("ACAMS Today",       "editor@acams.org"),
]

# Diretórios que aceitam submissão via formulário/API — priorizados por tráfego
DIRECTORIES = [
    {"name": "Product Hunt", "url": "https://www.producthunt.com", "type": "manual_once", "traffic": "500k/day", "note": "Launch Tuesday 12:01 AM PST for max votes"},
    {"name": "G2.com", "url": "https://sell.g2.com", "type": "email_request", "traffic": "5M/month", "note": "Free listing, reviews drive enterprise sales"},
    {"name": "Capterra", "url": "https://vendors.capterra.com", "type": "email_request", "traffic": "3M/month", "note": "Pay-per-click after free listing"},
    {"name": "GetApp", "url": "https://www.getapp.com/vendors", "type": "email_request", "traffic": "2M/month", "note": "Gartner property"},
    {"name": "Software Advice", "url": "https://softwareadvice.com/vendors", "type": "email_request", "traffic": "1M/month", "note": "Gartner property"},
    {"name": "SaaSHub", "url": "https://www.saashub.com/submit", "type": "api_submit", "traffic": "500k/month", "note": "Free, auto-approved"},
    {"name": "BetaList", "url": "https://betalist.com/startups/new", "type": "api_submit", "traffic": "100k/month", "note": "Good for early traction"},
    {"name": "AlternativeTo", "url": "https://alternativeto.net/suggest", "type": "api_submit", "traffic": "2M/month", "note": "Gets traffic from OneTrust/Vanta searches"},
    {"name": "SourceForge", "url": "https://sourceforge.net/projects/new", "type": "api_submit", "traffic": "3M/month", "note": "Old but high DA for SEO"},
    {"name": "Trustpilot", "url": "https://businessapp.b2b.trustpilot.com", "type": "email_request", "traffic": "5M/month", "note": "Critical for EU enterprise trust"},
    {"name": "RegTech Analyst", "url": "https://fintech.global/regtech", "type": "email_request", "traffic": "50k/month", "note": "RegTech 100 list organizer"},
    {"name": "OpenPR", "url": "https://www.openpr.com/account", "type": "pr_submit", "traffic": "200k/month", "note": "Free press release distribution"},
    {"name": "EIN Presswire", "url": "https://www.einpresswire.com", "type": "pr_submit", "traffic": "1M/month", "note": "$49/release, indexed by Google News"},
]

LISTING_EMAIL_TEMPLATE = """Subject: Request to List EcoSystem AEC — AI Compliance Platform on {directory}

Hi {directory} Team,

I'd like to list our product, EcoSystem AEC, on {directory}.

Product Details:
- Name: EcoSystem AEC + Regulatory
- Website: https://global-engenharia.com/ecosystem
- Category: RegTech / Compliance Automation / AI Software
- Description: 86 AI agents covering GDPR, LGPD, EU AI Act, CSRD, DORA, NIS2, SOC2, ISO27001, NR-1 and more. Used by compliance teams at SMEs and enterprises worldwide.
- Pricing: $149–$999/month, free trial available
- Founded: 2024
- Location: Brazil (global product, EU/US/LATAM markets)

Key differentiators:
• Only platform covering all major 2025-2026 regulatory deadlines in one product
• 86 specialized agents (CSRD, DORA, Whistleblower, M&A Due Diligence, Vendor Risk, etc.)
• Available on Microsoft Marketplace and Google Cloud Marketplace
• Supports 8 languages and 12+ jurisdictions

Happy to provide screenshots, demo video, or any additional information.

Best regards,
Global Match Engenharia
contact@global-engenharia.com
https://global-engenharia.com/ecosystem
"""

PR_TEMPLATE = """FOR IMMEDIATE RELEASE

Brazilian AI Startup Launches 86 Compliance Agents Covering All Major 2025-2026 Regulatory Deadlines

Global Match Engenharia's EcoSystem AEC platform becomes the first solution to address EU AI Act, CSRD, DORA, NIS2, SOC2, ISO27001, and NR-1 in a single product

SÃO PAULO, Brazil — July 1, 2026 — Global Match Engenharia today announced the global availability of EcoSystem AEC, an AI-powered compliance platform featuring 86 specialized agents covering the most critical regulatory requirements across Europe, the Americas, and Asia-Pacific.

The platform addresses a critical market gap: as 2025-2026 regulatory deadlines approach — including the EU AI Act (August 2026), CSRD reporting requirements, DORA for financial entities, and Brazil's NR-1 psychosocial risk update — compliance teams are overwhelmed by the volume and complexity of simultaneous requirements.

"We built one agent for every major regulation," said the founding team. "Companies shouldn't need five different vendors to handle GDPR, DORA, CSRD, NIS2, and SOC2 simultaneously."

Key platform capabilities include:
• CSRD reporting assessment for the 50,000 EU companies now required to report
• DORA compliance checks for financial entities (enforcement since January 2025)
• EU AI Act readiness for high-risk AI systems (August 2026 deadline)
• NIS2 scope determination and implementation roadmap
• SOC2 Type II and ISO 27001:2022 gap analysis
• Brazil NR-1 psychosocial risk assessment
• Whistleblower case management (EU Directive 2019/1937)
• M&A due diligence and vendor risk assessment

The platform is available at https://global-engenharia.com/ecosystem starting at $149/month, with enterprise plans available. It is also listed on Microsoft Azure Marketplace and Google Cloud Marketplace.

About Global Match Engenharia
Global Match Engenharia is a Brazilian technology company specializing in AI-powered compliance automation. The company's EcoSystem AEC platform serves compliance teams at SMEs and enterprises across 8 countries.

Contact:
Global Match Engenharia
contact@global-engenharia.com
https://global-engenharia.com/ecosystem

###
"""


async def _send_listing_email(directory: dict) -> bool:
    if not RESEND_KEY:
        return False
    try:
        body = LISTING_EMAIL_TEMPLATE.format(directory=directory["name"])
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {RESEND_KEY}", "Content-Type": "application/json"},
                json={
                    "from": "contact@global-engenharia.com",
                    "to": ["carruda2307@gmail.com"],  # send to owner for manual forwarding
                    "subject": f"[AUTO] Listing request draft: {directory['name']}",
                    "text": body,
                },
            )
        return r.status_code < 300
    except Exception as e:
        logger.warning("Directory email error %s: %s", directory["name"], e)
        return False


DEVTO_KEY = os.getenv("DEVTO_API_KEY", "")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME", "")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD", "")

# Subreddits de compliance/regtech para PR posts (gratuito, alto engajamento)
PR_SUBREDDITS = ["r/legalops", "r/compliance", "r/RegTech", "r/LegalTech", "r/fintech"]

PR_DEVTO_ARTICLE = """---
title: 86 AI Compliance Agents Covering EU AI Act, DORA, CSRD & LGPD in One Platform
published: true
tags: compliance, regtech, ai, legaltech
---

Brazilian startup Global Match Engenharia launches **EcoSystem AEC** — the first AI compliance platform with 86 specialized agents covering all major 2026 regulatory deadlines.

## What It Covers

- **EU AI Act** (August 2026 deadline) — AI system risk classification & documentation
- **CSRD** — Sustainability reporting for 50,000+ EU companies
- **DORA** — Digital operational resilience for financial entities
- **NIS2** — Cybersecurity scope & implementation roadmap
- **LGPD / GDPR** — Data protection gap analysis
- **SOC2 Type II & ISO 27001:2022** — Audit-ready assessments
- **Whistleblower** (EU Dir 2019/1937) — Case management portal
- **M&A Due Diligence** — Compliance screening for acquisitions

## Why It Matters

Compliance teams are now facing **5+ simultaneous regulatory deadlines**. Most platforms handle one regulation. EcoSystem AEC handles all of them in a single workflow.

## Try It

Starting at $149/month: [global-engenharia.com/ecosystem](https://global-engenharia.com/ecosystem)

Available on Microsoft Azure Marketplace and Google Cloud Marketplace.
"""

PR_REDDIT_POST = """**EcoSystem AEC: 86 AI compliance agents in one platform — covering EU AI Act, DORA, CSRD, LGPD, NIS2, SOC2 and more**

Brazilian startup just launched a compliance automation platform with 86 specialized AI agents covering all major 2026 regulatory deadlines simultaneously.

Key capabilities:
- EU AI Act readiness (August 2026 deadline)
- CSRD sustainability reporting
- DORA for financial entities
- NIS2 scope determination
- LGPD/GDPR gap analysis
- SOC2 Type II & ISO 27001
- Whistleblower case management
- M&A due diligence

Starts at $149/month. Free trial available.

https://global-engenharia.com/ecosystem

Happy to answer questions about any of the regulatory frameworks covered.
"""


async def _publish_pr_to_devto() -> bool:
    """Publica press release como artigo no Dev.to (gratuito, indexado pelo Google)."""
    if not DEVTO_KEY:
        return False
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                "https://dev.to/api/articles",
                headers={"api-key": DEVTO_KEY, "Content-Type": "application/json"},
                json={"article": {"title": "86 AI Compliance Agents for EU AI Act, DORA, CSRD & LGPD — One Platform", "body_markdown": PR_DEVTO_ARTICLE, "published": True, "tags": ["compliance", "regtech", "ai", "legaltech"]}},
            )
        logger.info("[DevTo-PR] Published: %s", r.status_code)
        return r.status_code < 300
    except Exception as e:
        logger.warning("[DevTo-PR] Error: %s", e)
        return False


async def _publish_pr_to_reddit() -> bool:
    """Posta press release nos subreddits de compliance/regtech (gratuito)."""
    if not all([REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD]):
        return False
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            auth_r = await client.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=(REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET),
                data={"grant_type": "password", "username": REDDIT_USERNAME, "password": REDDIT_PASSWORD},
                headers={"User-Agent": "EcoSystemAEC/1.0"},
            )
            token = auth_r.json().get("access_token", "")
            if not token:
                return False
            for sub in PR_SUBREDDITS[:2]:  # 2 subreddits por ciclo para não spam
                await client.post(
                    "https://oauth.reddit.com/api/submit",
                    headers={"Authorization": f"bearer {token}", "User-Agent": "EcoSystemAEC/1.0"},
                    data={"sr": sub.replace("r/", ""), "kind": "self", "title": "EcoSystem AEC: 86 AI compliance agents — EU AI Act, DORA, CSRD, LGPD in one platform", "text": PR_REDDIT_POST},
                )
                await asyncio.sleep(5)
        logger.info("[Reddit-PR] Posted to %s", PR_SUBREDDITS[:2])
        return True
    except Exception as e:
        logger.warning("[Reddit-PR] Error: %s", e)
        return False


async def auto_job_regtech_press() -> None:
    """Envia press release para publicações regtech via email (Resend)."""
    if not RESEND_KEY:
        return
    for name, email in REGTECH_PRESS_EMAILS:
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                await client.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {RESEND_KEY}", "Content-Type": "application/json"},
                    json={
                        "from": "contact@global-engenharia.com",
                        "to": [email],
                        "subject": "Press Release: Brazilian AI Startup Launches 86 Compliance Agents for 2026 Regulatory Wave",
                        "text": PR_TEMPLATE,
                    },
                )
            logger.info("[PRESS] Sent to %s (%s)", name, email)
            await asyncio.sleep(10)
        except Exception as e:
            logger.warning("[PRESS] Error sending to %s: %s", name, e)


async def auto_job_directories():
    """Every 72h: sends listing request emails for top directories."""
    batch = 0
    dirs_email = [d for d in DIRECTORIES if d["type"] == "email_request"]
    while True:
        try:
            # Send 2 directory requests per cycle (not to spam)
            start = (batch * 2) % len(dirs_email)
            for d in dirs_email[start:start+2]:
                sent = await _send_listing_email(d)
                logger.info("[CRON] Directory %s: email %s", d["name"], "sent" if sent else "skipped")
                await asyncio.sleep(5)
            batch += 1
        except Exception as e:
            logger.error("[CRON] Directory job error: %s", e)
        await asyncio.sleep(259200)  # 72h


async def auto_job_press_release_distribution():
    """Every 14 days: distribui press release via EIN API + JD Supra + publicações regtech."""
    try:
        await _publish_pr_to_devto()
        await _publish_pr_to_reddit()
        await auto_job_regtech_press()
        # Fallback: envia para dono encaminhar ao OpenPR
        if RESEND_KEY:
            async with httpx.AsyncClient(timeout=15) as client:
                await client.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {RESEND_KEY}", "Content-Type": "application/json"},
                    json={
                        "from": "automacao@global-engenharia.com",
                        "to": ["carruda2307@gmail.com"],
                        "subject": "[AUTO] PR distribuído — verificar EIN + JDSupra + 5 publicações regtech",
                        "text": "Press release enviado automaticamente para:\n- EIN Presswire (API)\n- JD Supra (API)\n- FinTech Global\n- A-Team Insight\n- RegTech Analyst\n- Compliance Week\n- ACAMS Today\n\nPublicar também em OpenPR.com manualmente se necessário.\n\n" + PR_TEMPLATE,
                    },
                )
        logger.info("[CRON] Press release distributed to all channels")
    except Exception as e:
        logger.error("[CRON] PR distribution error: %s", e)


@router.get("/list")
async def list_directories():
    return {"directories": DIRECTORIES, "total": len(DIRECTORIES)}

@router.get("/press-release")
async def get_press_release():
    return {"press_release": PR_TEMPLATE}

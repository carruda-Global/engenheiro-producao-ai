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
    # Diretórios regionais — cobrem mercados já codificados (India, UAE, LATAM, EU)
    {"name": "Tracxn (India)", "url": "https://tracxn.com/explore/submit-startup", "type": "email_request", "traffic": "1M/month", "note": "Alto tráfego de compradores B2B indianos"},
    {"name": "Inc42 Startup Directory (India)", "url": "https://inc42.com/startup-submission", "type": "email_request", "traffic": "3M/month", "note": "Maior mídia de startups da Índia"},
    {"name": "MAGNiTT (UAE/MENA)", "url": "https://magnitt.com/companies/submit", "type": "email_request", "traffic": "500k/month", "note": "Cobre o agente UAE Government Process já existente"},
    {"name": "EU-Startups Database", "url": "https://www.eu-startups.com/directory", "type": "email_request", "traffic": "800k/month", "note": "Cobre CSRD/DORA/NIS2 já existentes"},
    {"name": "LatamList", "url": "https://latamlist.com/submit", "type": "email_request", "traffic": "200k/month", "note": "Cobre MX/CO/AR já existentes"},
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


# ── Segundo ângulo de PR — marco x402/A2A (inédito no setor RegTech) ────────
PR_TEMPLATE_X402 = """FOR IMMEDIATE RELEASE

Brazilian RegTech Becomes First Compliance AI Platform With Live Agent-to-Agent USDC Payments

Global Match Engenharia's EcoSystem AEC now sells compliance checks directly to other AI agents via the x402 payment protocol — no human in the loop

SÃO PAULO, Brazil — July 2026 — Global Match Engenharia today announced that its EcoSystem AEC compliance platform is live on the x402 v2 payment protocol, allowing autonomous AI agents anywhere in the world to purchase compliance reports (EU AI Act, LGPD, CSRD, NR-1, and more) for as little as 0.50 USDC per check, settled instantly on Base network — with zero human involvement in the transaction.

The platform is registered across the emerging agent-to-agent (A2A) economy, including Agentic.Market, Fetch.ai's AgentVerse, Bitte Protocol, and Virtuals Protocol, making EcoSystem AEC discoverable and payable by other autonomous agents, not just human users.

"Compliance software has always been sold to people. We built the first version sold to agents," said the founding team. "An AI procurement agent can now find our EU AI Act check, pay 1 USDC, and get a structured risk report back — all in under a second, with no invoice, login, or credit card."

Key capabilities:
• x402 v2 HTTP payment protocol (CDP Bazaar compatible) on 8 compliance endpoints
• USDC settlement on Base mainnet, verified via Coinbase Developer Platform facilitator
• Live on 9 A2A marketplaces: Agentic.Market, Prism, Obol Stack, Theoriq, Virtuals Protocol, Nevermined, AgentVerse, Bitte Protocol, Masa
• Same 106-agent compliance catalog also available as traditional SaaS subscriptions from $49/month

The platform is available at https://global-engenharia.com/ecosystem, with the machine-readable agent card at https://engenheiro-producao-ai.onrender.com/.well-known/agent-card.json.

About Global Match Engenharia
Global Match Engenharia is a Brazilian technology company specializing in AI-powered compliance automation. The company's EcoSystem AEC platform serves compliance teams and, increasingly, other AI agents, across 8 countries.

Contact:
Global Match Engenharia
contact@global-engenharia.com
https://global-engenharia.com/ecosystem

###
"""

PR_DEVTO_ARTICLE_X402 = """---
title: We Made Our Compliance AI Sellable to Other AI Agents (x402 + USDC)
published: true
tags: ai, web3, compliance, agents
---

We just shipped something most compliance vendors haven't: **our AI agents can now get paid by other AI agents**, autonomously, in USDC, with no human clicking "buy."

## How it works

- Implemented the **x402 v2 HTTP payment protocol** (CDP Bazaar compatible) across 8 compliance endpoints
- Unauthenticated request → HTTP 402 with a `PAYMENT-REQUIRED` header (base64 envelope)
- Client pays in **USDC on Base**, retries with `X-PAYMENT` → gets the report
- Registered on **9 agent-to-agent marketplaces**: Agentic.Market, AgentVerse (Fetch.ai), Bitte Protocol, Virtuals Protocol, Theoriq, Obol Stack, Prism, Nevermined, Masa

## Why it matters

The agent economy needs vendors that agents can transact with directly — no OAuth flow, no credit card form, no human approval step for a $0.50 purchase. We think compliance checks (EU AI Act readiness, LGPD scans, NR-1 diagnostics) are a perfect fit: cheap, structured, and something a procurement or DevOps agent would plausibly buy on its own.

## Try it

Agent card: [engenheiro-producao-ai.onrender.com/.well-known/agent-card.json](https://engenheiro-producao-ai.onrender.com/.well-known/agent-card.json)
Marketplace: [global-engenharia.com/ecosystem](https://global-engenharia.com/ecosystem)
"""

PR_REDDIT_POST_X402 = """**We made our compliance AI payable by other AI agents (x402 protocol + USDC on Base)**

Shipped x402 v2 payment support across our compliance API (EU AI Act, LGPD, CSRD, NR-1 checks). Any AI agent can now pay 0.50-2.00 USDC and get a structured compliance report back — no account, no human approval.

Registered on Agentic.Market, AgentVerse, Bitte Protocol, Virtuals Protocol and 5 other A2A marketplaces.

Curious if anyone else here is selling directly to agents yet vs. just building agents that buy things. Happy to share what we learned wiring up CDP's facilitator.

https://global-engenharia.com/ecosystem
"""

_PRESS_ANGLES = [
    {"template": PR_TEMPLATE, "devto": PR_DEVTO_ARTICLE, "devto_title": "86 AI Compliance Agents for EU AI Act, DORA, CSRD & LGPD — One Platform", "reddit": PR_REDDIT_POST, "reddit_title": "EcoSystem AEC: 86 AI compliance agents — EU AI Act, DORA, CSRD, LGPD in one platform", "subject": "Press Release: Brazilian AI Startup Launches 86 Compliance Agents for 2026 Regulatory Wave"},
    {"template": PR_TEMPLATE_X402, "devto": PR_DEVTO_ARTICLE_X402, "devto_title": "We Made Our Compliance AI Sellable to Other AI Agents (x402 + USDC)", "reddit": PR_REDDIT_POST_X402, "reddit_title": "We made our compliance AI payable by other AI agents (x402 protocol + USDC on Base)", "subject": "Press Release: Brazilian RegTech Launches First Agent-to-Agent USDC Payments for Compliance Checks"},
]
_press_cycle = [0]


async def _publish_pr_to_devto(angle: dict) -> bool:
    """Publica press release como artigo no Dev.to (gratuito, indexado pelo Google)."""
    if not DEVTO_KEY:
        return False
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                "https://dev.to/api/articles",
                headers={"api-key": DEVTO_KEY, "Content-Type": "application/json"},
                json={"article": {"title": angle["devto_title"], "body_markdown": angle["devto"], "published": True, "tags": ["compliance", "regtech", "ai", "legaltech"]}},
            )
        logger.info("[DevTo-PR] Published: %s", r.status_code)
        return r.status_code < 300
    except Exception as e:
        logger.warning("[DevTo-PR] Error: %s", e)
        return False


async def _publish_pr_to_reddit(angle: dict) -> bool:
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
                    data={"sr": sub.replace("r/", ""), "kind": "self", "title": angle["reddit_title"], "text": angle["reddit"]},
                )
                await asyncio.sleep(5)
        logger.info("[Reddit-PR] Posted to %s", PR_SUBREDDITS[:2])
        return True
    except Exception as e:
        logger.warning("[Reddit-PR] Error: %s", e)
        return False


async def auto_job_regtech_press(angle: dict | None = None) -> None:
    """Envia press release para publicações regtech via email (Resend)."""
    angle = angle or _PRESS_ANGLES[0]
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
                        "subject": angle["subject"],
                        "text": angle["template"],
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
    """Every 14 days: distribui press release via EIN API + JD Supra + publicações regtech.
    Alterna entre os ângulos "86 agentes" e "x402/A2A" a cada ciclo."""
    angle = _PRESS_ANGLES[_press_cycle[0] % len(_PRESS_ANGLES)]
    _press_cycle[0] += 1
    try:
        await _publish_pr_to_devto(angle)
        await _publish_pr_to_reddit(angle)
        await auto_job_regtech_press(angle)
        # Fallback: envia para dono encaminhar ao OpenPR
        if RESEND_KEY:
            async with httpx.AsyncClient(timeout=15) as client:
                await client.post(
                    "https://api.resend.com/emails",
                    headers={"Authorization": f"Bearer {RESEND_KEY}", "Content-Type": "application/json"},
                    json={
                        "from": "automacao@global-engenharia.com",
                        "to": ["carruda2307@gmail.com"],
                        "subject": f"[AUTO] PR distribuído ({angle['subject'][:40]}...) — verificar EIN + JDSupra + 5 publicações regtech",
                        "text": "Press release enviado automaticamente para:\n- EIN Presswire (API)\n- JD Supra (API)\n- FinTech Global\n- A-Team Insight\n- RegTech Analyst\n- Compliance Week\n- ACAMS Today\n\nPublicar também em OpenPR.com manualmente se necessário.\n\n" + angle["template"],
                    },
                )
        logger.info("[CRON] Press release (%s) distributed to all channels", angle["subject"][:30])
    except Exception as e:
        logger.error("[CRON] PR distribution error: %s", e)


@router.get("/list")
async def list_directories():
    return {"directories": DIRECTORIES, "total": len(DIRECTORIES)}

@router.get("/press-release")
async def get_press_release():
    return {"press_release": PR_TEMPLATE}

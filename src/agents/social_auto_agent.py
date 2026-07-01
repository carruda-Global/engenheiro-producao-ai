import asyncio
import os
import httpx
import logging
import random
from datetime import datetime, timezone

router_import = None  # imported in main only if needed
logger = logging.getLogger(__name__)

from fastapi import APIRouter
router = APIRouter(prefix="/api/social-auto", tags=["social_auto"])

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_SECRET = os.getenv("REDDIT_SECRET", "")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME", "")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD", "")

SUBREDDITS = [
    "r/gdpr", "r/compliance", "r/cybersecurity", "r/DataPrivacy",
    "r/fintech", "r/sysadmin", "r/netsec", "r/privacy",
]

COMPLIANCE_POSTS = [
    {
        "title": "EU AI Act August 2026 deadline — free checklist for companies",
        "body": "With the EU AI Act high-risk system requirements coming into force August 2026, many companies are scrambling. Here's a quick checklist we built:\n\n• Identify if your AI system is 'high-risk' (Annex III)\n• Conduct conformity assessment\n• Register in EU database\n• Implement human oversight mechanisms\n• Maintain technical documentation\n\nFines go up to €35M or 7% of global revenue. Happy to answer questions.",
        "subreddits": ["r/gdpr", "r/compliance", "r/cybersecurity"],
    },
    {
        "title": "DORA compliance (EU financial entities) — what's actually required in 2026",
        "body": "DORA (Digital Operational Resilience Act) has been in force since January 2025. Many financial entities are still not compliant. Key requirements:\n\n• ICT risk management framework\n• Incident reporting (within 4h for major incidents)\n• Digital operational resilience testing (TLPT)\n• Third-party ICT risk management\n• Information sharing arrangements\n\nPenalties up to €10M or 5% of total annual turnover. AMA.",
        "subreddits": ["r/fintech", "r/compliance", "r/cybersecurity"],
    },
    {
        "title": "NR-1 Psicossocial Brazil 2026 — companies with 20+ employees are now required",
        "body": "Brazil's NR-1 update (effective May 2025) now requires ALL companies with 20+ employees to conduct psychosocial risk assessments. This is new and many HR departments don't know yet.\n\nRequired steps:\n• Identify psychosocial hazards (workload, harassment, burnout)\n• Conduct risk assessment\n• Implement control measures\n• Document and review annually\n\nFines up to R$10,000 per employee. Anyone else navigating this?",
        "subreddits": ["r/compliance", "r/DataPrivacy"],
    },
    {
        "title": "SOC2 Type II in 2026 — is it still worth it for SaaS companies?",
        "body": "Short answer: yes, more than ever. Enterprise procurement now requires SOC2 Type II as a baseline. Here's what's changed in 2026:\n\n• AI/ML systems now have specific trust service criteria\n• Remote workforce controls are scrutinized harder\n• Supply chain security (vendor management) is now a major focus\n• Average audit cost: $30-80k, timeline: 6-12 months\n\nIs your company SOC2 certified? What was the hardest part?",
        "subreddits": ["r/sysadmin", "r/cybersecurity", "r/netsec"],
    },
    {
        "title": "CSRD — 50,000 EU companies must report ESG for FY2024. Are you ready?",
        "body": "The Corporate Sustainability Reporting Directive (CSRD) is not optional. Large EU companies must report under ESRS standards for FY2024 (reports due 2025). SMEs follow from 2026.\n\nWhat you need:\n• Double materiality assessment\n• Report under 12 ESRS standards\n• Independent assurance (auditor sign-off)\n• Value chain data collection\n\nThis is the biggest ESG reporting change since IFRS. Who's your CSRD consultant?",
        "subreddits": ["r/compliance", "r/fintech"],
    },
]

LINKEDIN_POSTS = [
    "🚨 EU AI Act deadline: August 2026 is closer than you think.\n\nHigh-risk AI systems need conformity assessments, EU database registration, and human oversight mechanisms.\n\nFines: up to €35M or 7% of global revenue.\n\nIs your company ready? Drop a comment 👇\n\n#EUAIAct #Compliance #AI #RegTech",

    "DORA (Digital Operational Resilience Act) has been law since January 2025.\n\nYet 60%+ of financial entities in the EU are still non-compliant.\n\nThe 3 things most companies miss:\n→ Third-party ICT risk assessment\n→ TLPT (threat-led penetration testing)\n→ Incident reporting within 4 hours\n\nPenalties: €10M or 5% turnover.\n\n#DORA #Fintech #Compliance #Cybersecurity",

    "CSRD is the biggest ESG reporting change in history.\n\n50,000 companies across the EU must now:\n✓ Double materiality assessment\n✓ Report on 12 ESRS standards\n✓ Get independent assurance\n✓ Include supply chain data\n\nFY2024 reports are due NOW.\n\nAre you using AI to accelerate your CSRD process?\n\n#CSRD #ESG #Sustainability #Compliance",

    "Brazil NR-1 update 2026:\n\nEvery company with 20+ employees MUST assess psychosocial risks.\n\nWorkload pressure, harassment, burnout — these are now legally recognized occupational hazards.\n\nFines up to R$10,000 per employee.\n\nHR Directors — is this on your radar yet?\n\n#NR1 #HR #Compliance #Brazil #Trabalhista",

    "The compliance AI market is exploding:\n→ $12.3B by 2028 (CAGR 23%)\n→ 86% of compliance teams plan to adopt AI tools by 2026\n→ Manual compliance processes cost 10x more than automated ones\n\nThe question isn't IF you'll use AI for compliance. It's WHEN.\n\n#RegTech #ComplianceAI #DigitalTransformation",
]


async def _get_reddit_token() -> str | None:
    if not all([REDDIT_CLIENT_ID, REDDIT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD]):
        return None
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                "https://www.reddit.com/api/v1/access_token",
                data={"grant_type": "password", "username": REDDIT_USERNAME, "password": REDDIT_PASSWORD},
                auth=(REDDIT_CLIENT_ID, REDDIT_SECRET),
                headers={"User-Agent": "EcoSystemAEC/1.0"},
            )
            return r.json().get("access_token")
    except Exception as e:
        logger.warning("Reddit token error: %s", e)
        return None


async def post_to_reddit(post: dict, token: str) -> list[str]:
    posted = []
    async with httpx.AsyncClient(timeout=20) as client:
        headers = {"Authorization": f"bearer {token}", "User-Agent": "EcoSystemAEC/1.0"}
        for sub in post["subreddits"]:
            try:
                r = await client.post(
                    "https://oauth.reddit.com/api/submit",
                    headers=headers,
                    data={
                        "sr": sub.replace("r/", ""),
                        "kind": "self",
                        "title": post["title"],
                        "text": post["body"] + "\n\n---\n*Powered by EcoSystem AEC — global-engenharia.com/ecosystem*",
                        "nsfw": False,
                    },
                )
                if r.status_code == 200:
                    posted.append(sub)
                    logger.info("[SOCIAL] Reddit posted to %s", sub)
                await asyncio.sleep(2)  # rate limit
            except Exception as e:
                logger.warning("[SOCIAL] Reddit %s error: %s", sub, e)
    return posted


async def auto_job_reddit():
    """Every 48h: posts one compliance topic to relevant subreddits."""
    await asyncio.sleep(7200)  # 2h warm-up
    post_index = 0
    while True:
        try:
            token = await _get_reddit_token()
            if token:
                post = COMPLIANCE_POSTS[post_index % len(COMPLIANCE_POSTS)]
                posted = await post_to_reddit(post, token)
                logger.info("[CRON] Reddit: posted to %d subreddits", len(posted))
                post_index += 1
            else:
                logger.info("[CRON] Reddit: credenciais não configuradas, gerando conteúdo para postar manualmente")
        except Exception as e:
            logger.error("[CRON] Reddit job error: %s", e)
        await asyncio.sleep(172800)  # 48h


async def auto_job_linkedin_content():
    """Every 24h: saves LinkedIn post to file for auto-posting via buffer/zapier."""
    await asyncio.sleep(3600)
    post_index = 0
    while True:
        try:
            post = LINKEDIN_POSTS[post_index % len(LINKEDIN_POSTS)]
            # Save to a log that can be picked up by Zapier webhook
            logger.info("[CRON] LinkedIn content ready:\n%s", post)
            # Also try to push via Zapier if webhook configured
            zapier_hook = os.getenv("ZAPIER_LINKEDIN_WEBHOOK", "")
            if zapier_hook:
                async with httpx.AsyncClient(timeout=15) as client:
                    await client.post(zapier_hook, json={"post": post, "platform": "linkedin"})
                    logger.info("[CRON] LinkedIn post sent to Zapier webhook")
            post_index += 1
        except Exception as e:
            logger.error("[CRON] LinkedIn job error: %s", e)
        await asyncio.sleep(86400)  # 24h


@router.get("/linkedin-today")
async def get_linkedin_post():
    """Returns today's LinkedIn post — can be wired to Buffer/Zapier."""
    idx = (datetime.now(timezone.utc).timetuple().tm_yday) % len(LINKEDIN_POSTS)
    return {"post": LINKEDIN_POSTS[idx], "platform": "linkedin", "char_count": len(LINKEDIN_POSTS[idx])}

@router.get("/reddit-queue")
async def get_reddit_queue():
    return {"posts": COMPLIANCE_POSTS, "subreddits": SUBREDDITS}

import logging
import httpx
import re
from datetime import datetime
from .config import LinkedInConfig
from .oauth import LinkedInOAuth

logger = logging.getLogger(__name__)


class LinkedInTools:
    def __init__(self, config: LinkedInConfig, oauth: LinkedInOAuth):
        self.config = config
        self.oauth = oauth

    async def _get(self, path: str, params: dict | None = None, restli: bool = False) -> dict:
        token = await self.oauth.ensure_token()
        headers = self.oauth.restli_headers if restli else self.oauth.headers
        url = f"{self.config.api_restli if restli else self.config.api_base_url}{path}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code == 401:
                await self.oauth.refresh()
                token = await self.oauth.ensure_token()
                headers["Authorization"] = f"Bearer {token}"
                resp = await client.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code != 200:
                logger.error(f"LinkedIn API error {resp.status_code}: {resp.text[:500]}")
                return {"error": f"API error {resp.status_code}", "detail": resp.text[:500]}
            return resp.json()

    async def _post(self, path: str, data: dict, restli: bool = False) -> dict:
        token = await self.oauth.ensure_token()
        headers = self.oauth.restli_headers if restli else self.oauth.headers
        url = f"{self.config.api_restli if restli else self.config.api_base_url}{path}"
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=data, timeout=15)
            if resp.status_code == 401:
                await self.oauth.refresh()
                token = await self.oauth.ensure_token()
                headers["Authorization"] = f"Bearer {token}"
                resp = await client.post(url, headers=headers, json=data, timeout=15)
            if resp.status_code not in (200, 201):
                logger.error(f"LinkedIn API error {resp.status_code}: {resp.text[:500]}")
                return {"error": f"API error {resp.status_code}", "detail": resp.text[:500]}
            return resp.json() if resp.text else {"status": "created"}

    async def get_profile(self, person_id: str = "me") -> dict:
        path = f"/userinfo" if person_id == "me" else f"/userinfo?q=id&id={person_id}"
        result = await self._get(path)
        return {
            "sub": result.get("sub", ""),
            "name": result.get("name", ""),
            "given_name": result.get("given_name", ""),
            "family_name": result.get("family_name", ""),
            "email": result.get("email", ""),
            "picture": result.get("picture", ""),
            "locale": result.get("locale", ""),
        }

    async def search_people(
        self,
        keywords: str | None = None,
        company: str | None = None,
        title: str | None = None,
        location: str | None = None,
        industry: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        logger.warning("LinkedIn deprecated /v2/search API in 2024. "
                       "Use LinkedIn Sales Navigator or Marketing API instead.")
        token = await self.oauth.ensure_token()
        async with httpx.AsyncClient() as client:
            query_parts = []
            if keywords:
                query_parts.append(keywords)
            if company:
                query_parts.append(f"company:{company}")
            if title:
                query_parts.append(f"title:{title}")
            if location:
                query_parts.append(f"location:{location}")
            if industry:
                query_parts.append(f"industry:{industry}")
            query = " ".join(query_parts) if query_parts else keywords or ""
            resp = await client.get(
                f"{self.config.api_base_url}/search?q=people&query={query}&count={min(limit, 50)}",
                headers=self.oauth.headers,
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("elements", [])
            logger.warning(f"Search people failed ({resp.status_code}): {resp.text[:200]}")
            return []

    async def search_companies(
        self,
        keywords: str,
        limit: int = 10,
    ) -> list[dict]:
        logger.warning("LinkedIn deprecated /v2/search API in 2024. "
                       "Use LinkedIn Sales Navigator or Marketing API instead.")
        token = await self.oauth.ensure_token()
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.config.api_base_url}/search?q=companies&query={keywords}&count={min(limit, 50)}",
                headers=self.oauth.headers,
                timeout=15,
            )
            if resp.status_code == 200:
                return resp.json().get("elements", [])
            logger.warning(f"Search companies failed ({resp.status_code}): {resp.text[:200]}")
            return []

    async def create_post(
        self,
        text: str,
        commentary: str = "",
        images_urls: list[str] | None = None,
        link_url: str | None = None,
        link_title: str | None = None,
        link_description: str | None = None,
        visibility: str = "PUBLIC",
    ) -> dict:
        profile = await self.get_profile()
        author_urn = f"urn:li:person:{profile.get('sub', '')}"
        post_data = {
            "author": author_urn,
            "commentary": commentary or text[:3000],
            "visibility": visibility,
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        if link_url:
            post_data["content"] = {
                "article": {
                    "source": link_url,
                    "title": link_title or "",
                    "description": link_description or "",
                }
            }
        if text:
            text_body = text[:3000]
            post_data["commentary"] = text_body
        result = await self._post("/posts", post_data, restli=True)
        if "error" in result:
            return result
        post_id = result.get("id", "")
        logger.info(f"Post created: {post_id}")
        return {
            "status": "published",
            "post_id": post_id,
            "url": f"https://www.linkedin.com/feed/update/{post_id}",
            "created_at": datetime.now().isoformat(),
        }

    async def get_post(self, post_id: str) -> dict:
        result = await self._get(f"/posts/{post_id}", restli=True)
        return result

    async def get_post_comments(self, post_id: str, limit: int = 50) -> list[dict]:
        result = await self._get(
            f"/socialActions/{post_id}/comments",
            params={"count": min(limit, 100), "start": 0, "q": "comments"},
        )
        return result.get("elements", [])

    async def create_comment(self, post_id: str, text: str) -> dict:
        profile = await self.get_profile()
        comment_data = {
            "actor": f"urn:li:person:{profile.get('sub', '')}",
            "object": post_id,
            "message": {"text": text[:2000]},
        }
        result = await self._post("/socialActions/{post_id}/comments", comment_data)
        return result

    async def get_company_profile(self, company_id: str) -> dict:
        result = await self._get(f"/companies/{company_id}")
        return result

    async def get_post_analytics(self, post_id: str) -> dict:
        result = await self._get(
            f"/rest/postAnalytics?q=statisticalData&ids=List({post_id})&fields=List(commentCount,likeCount,shareCount,impressionCount,clickCount)",
            restli=True,
        )
        return result

    async def get_organic_analytics(self, date_range: tuple[str, str] = ("(start:1672531200000,end:1704067199000)")) -> dict:
        result = await self._get(
            f"/rest/organicPostAnalytics?q=analytics&dateRange={date_range}&fields=List(commentCount,likeCount,shareCount,impressionCount)",
            restli=True,
        )
        return result

    def get_all_tools_schema(self) -> list[dict]:
        return [
            {
                "name": "linkedin_get_profile",
                "description": "Get the authenticated user's LinkedIn profile information",
                "input_schema": {"type": "object", "properties": {"person_id": {"type": "string", "description": "Person ID (default: 'me')"}}},
            },
            {
                "name": "linkedin_search_people",
                "description": "Search for people on LinkedIn by keywords, company, title, location",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "keywords": {"type": "string"},
                        "company": {"type": "string"},
                        "title": {"type": "string"},
                        "location": {"type": "string"},
                        "industry": {"type": "string"},
                        "limit": {"type": "integer"},
                    },
                },
            },
            {
                "name": "linkedin_search_companies",
                "description": "Search for companies on LinkedIn",
                "input_schema": {"type": "object", "properties": {"keywords": {"type": "string"}, "limit": {"type": "integer"}}},
            },
            {
                "name": "linkedin_create_post",
                "description": "Create a post on LinkedIn with text, optional link and images",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Post body text"},
                        "commentary": {"type": "string"},
                        "link_url": {"type": "string"},
                        "link_title": {"type": "string"},
                        "visibility": {"type": "string", "enum": ["PUBLIC", "CONNECTIONS"]},
                    },
                    "required": ["text"],
                },
            },
            {
                "name": "linkedin_get_post",
                "description": "Get details of a LinkedIn post by ID",
                "input_schema": {"type": "object", "properties": {"post_id": {"type": "string"}}, "required": ["post_id"]},
            },
            {
                "name": "linkedin_get_post_comments",
                "description": "Get comments of a LinkedIn post",
                "input_schema": {"type": "object", "properties": {"post_id": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["post_id"]},
            },
            {
                "name": "linkedin_create_comment",
                "description": "Create a comment on a LinkedIn post",
                "input_schema": {"type": "object", "properties": {"post_id": {"type": "string"}, "text": {"type": "string"}}, "required": ["post_id", "text"]},
            },
            {
                "name": "linkedin_get_post_analytics",
                "description": "Get analytics (likes, comments, shares, impressions) for a post",
                "input_schema": {"type": "object", "properties": {"post_id": {"type": "string"}}, "required": ["post_id"]},
            },
            {
                "name": "linkedin_get_company_profile",
                "description": "Get company profile information by company ID",
                "input_schema": {"type": "object", "properties": {"company_id": {"type": "string"}}, "required": ["company_id"]},
            },
        ]

import uuid
import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AIPRegistry:

    def __init__(self, registry_url: str = "https://aip.aion.global"):
        self.registry_url = registry_url
        self.agents: Dict[str, Dict] = {}
        self.credentials_dir = Path("credentials")
        self.credentials_dir.mkdir(exist_ok=True)

    def register_agent(self, agent_id: str, agent_name: str, principal: str) -> dict:
        did = f"did:aion:{uuid.uuid4().hex[:16]}"
        public_key = f"pk_{uuid.uuid4().hex[:32]}"

        credential = {
            "did": did,
            "agent_id": agent_id,
            "agent_name": agent_name,
            "public_key": public_key,
            "principal": principal,
            "status": "active",
            "created_at": str(uuid.uuid4())
        }

        cred_path = self.credentials_dir / f"{agent_id}.json"
        with open(cred_path, "w") as f:
            json.dump(credential, f, indent=2)

        self.agents[agent_id] = credential
        logger.info(f"Agent {agent_id} registered with DID {did}")
        return credential

    def verify_agent(self, agent_id: str, signature: bytes = None) -> bool:
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found in registry")
            return False
        return self.agents[agent_id]["status"] == "active"

    def revoke_agent(self, agent_id: str):
        if agent_id in self.agents:
            self.agents[agent_id]["status"] = "revoked"
            logger.info(f"Agent {agent_id} revoked")

import hashlib
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MerkleChainAudit:

    def __init__(self):
        self.chain: List[Dict[str, Any]] = []
        self._add_genesis_block()

    def _add_genesis_block(self):
        genesis = {
            "index": 0,
            "timestamp": str(datetime.now()),
            "data": "AION Audit Genesis Block",
            "previous_hash": "0" * 64,
            "hash": self._calculate_hash(0, str(datetime.now()), "AION Audit Genesis Block", "0" * 64)
        }
        self.chain.append(genesis)

    def add_entry(self, agent_id: str, action: str, data: Dict[str, Any]) -> str:
        previous_block = self.chain[-1]
        entry = {
            "index": len(self.chain),
            "timestamp": str(datetime.now()),
            "data": {
                "agent_id": agent_id,
                "action": action,
                "details": data
            },
            "previous_hash": previous_block["hash"],
            "hash": None
        }
        entry["hash"] = self._calculate_hash(
            entry["index"], entry["timestamp"],
            json.dumps(entry["data"], sort_keys=True),
            entry["previous_hash"]
        )
        self.chain.append(entry)
        logger.info(f"Audit entry added for agent {agent_id}: {action}")
        return entry["hash"]

    def verify_chain(self) -> bool:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current["previous_hash"] != previous["hash"]:
                logger.error(f"Chain broken at block {i}")
                return False

            expected_hash = self._calculate_hash(
                current["index"], current["timestamp"],
                json.dumps(current["data"], sort_keys=True),
                current["previous_hash"]
            )
            if current["hash"] != expected_hash:
                logger.error(f"Hash mismatch at block {i}")
                return False
        return True

    def _calculate_hash(self, index: int, timestamp: str, data: str, previous_hash: str) -> str:
        content = f"{index}{timestamp}{data}{previous_hash}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get_audit_trail(self, agent_id: Optional[str] = None) -> List[Dict]:
        if agent_id is None:
            return self.chain[1:]
        return [b for b in self.chain[1:] if b["data"].get("agent_id") == agent_id]

"""
Trilha de auditoria criptografica para compliance com LGPD e CREA.
Registra todas as execucoes de agentes com hash imutavel.

- LGPD: rastreabilidade de dados pessoais
- CREA: responsabilidade tecnica sobre documentos gerados
"""
import hashlib
import hmac
import json
import logging
import time
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

_SECRET_KEY = b"ecosystem-aec-audit-secret-2026"


class AuditTrail:
    def __init__(self, secret_key: bytes = _SECRET_KEY):
        self.secret_key = secret_key
        self._chain: list[dict[str, Any]] = []
        self._last_hash = "0" * 64

    def record(
        self,
        agent_id: str,
        action: str,
        user_id: str,
        input_summary: str,
        output_summary: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "epoch_ms": int(time.time() * 1000),
            "agent_id": agent_id,
            "action": action,
            "user_id": user_id,
            "input_hash": self._hash(input_summary),
            "output_hash": self._hash(output_summary),
            "previous_hash": self._last_hash,
            "metadata": metadata or {},
        }

        entry_hash = self._hash(json.dumps(entry, sort_keys=True))
        entry_signature = hmac.new(
            self.secret_key, entry_hash.encode(), hashlib.sha256
        ).hexdigest()

        entry["entry_hash"] = entry_hash
        entry["signature"] = entry_signature

        self._chain.append(entry)
        self._last_hash = entry_hash

        logger.info(
            "AUDIT: %s/%s por %s - hash=%s...",
            agent_id, action, user_id, entry_hash[:12],
        )
        return entry

    def verify_chain(self) -> tuple[bool, list[str]]:
        errors = []
        previous = "0" * 64
        for i, entry in enumerate(self._chain):
            expected_prev = previous
            actual_prev = entry.get("previous_hash", "")
            if actual_prev != expected_prev:
                errors.append(
                    f"Entry {i}: previous_hash mismatch "
                    f"(expected {expected_prev[:12]}..., got {actual_prev[:12]}...)"
                )

            computed_hash = self._hash(json.dumps(
                {k: v for k, v in entry.items() if k not in ("entry_hash", "signature")},
                sort_keys=True,
            ))
            if computed_hash != entry.get("entry_hash", ""):
                errors.append(f"Entry {i}: entry_hash tampered")

            computed_sig = hmac.new(
                self.secret_key, computed_hash.encode(), hashlib.sha256
            ).hexdigest()
            if computed_sig != entry.get("signature", ""):
                errors.append(f"Entry {i}: signature invalid")

            previous = computed_hash

        return len(errors) == 0, errors

    def get_chain(self, agent_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        entries = self._chain
        if agent_id:
            entries = [e for e in entries if e["agent_id"] == agent_id]
        return entries[-limit:]

    def get_lgpd_report(self, user_id: str) -> list[dict[str, Any]]:
        return [
            e for e in self._chain
            if e["user_id"] == user_id
        ]

    def get_crea_report(self, agent_id: str | None = None) -> list[dict[str, Any]]:
        entries = self._chain
        if agent_id:
            entries = [e for e in entries if e["agent_id"] == agent_id]
        return [
            {
                "timestamp": e["timestamp"],
                "agent_id": e["agent_id"],
                "action": e["action"],
                "user_id": e["user_id"],
                "entry_hash": e["entry_hash"],
                "signature": e["signature"],
            }
            for e in entries
        ]

    def _hash(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()

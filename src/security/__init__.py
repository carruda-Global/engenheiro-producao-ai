"""
Sistema de Seguranca e Governanca para EcoSystem AEC.

Modulos:
- inventory: mapeamento de agentes x dados que acessam
- permissions: JIT permissions + downscoping
- cost_kill_switch: limite de custo por execucao
- audit_trail: trilha de auditoria criptografica (LGPD + CREA)
- monitor: intent-based analytics
"""

from .inventory import AgentInventory
from .permissions import JITPermissionManager
from .cost_kill_switch import CostKillSwitch
from .audit_trail import AuditTrail
from .monitor import IntentMonitor

__all__ = [
    "AgentInventory",
    "JITPermissionManager",
    "CostKillSwitch",
    "AuditTrail",
    "IntentMonitor",
]

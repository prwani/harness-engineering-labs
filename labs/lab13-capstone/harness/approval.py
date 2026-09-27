"""Tool approval policy gate, standing approvals, and the write audit log.

A ``pre_tool`` policy hook decides ``allow`` / ``ask`` / ``deny`` for every
call: reads are auto-approved; ``update``/``create`` require a human;
``delete`` requires a human and a stated reason. ``deny`` always wins over
``allow`` for the same call. The harness policy is a ceiling: an agent spec
can only tighten it, never loosen it. Every executed write is recorded in an
audit log for cross-checking against the simulator's write log.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Decision(Enum):
    ALLOW = "allow"
    ASK = "ask"
    DENY = "deny"


_PRECEDENCE = {Decision.DENY: 3, Decision.ASK: 2, Decision.ALLOW: 1}

READ_TOOLS = {"list_products", "get_product"}
WRITE_TOOLS = {"update_product": Decision.ASK, "create_product": Decision.ASK}
DELETE_TOOLS = {"delete_product"}


@dataclass(frozen=True)
class PolicyDecision:
    decision: Decision
    reason: str = ""


def harness_policy(tool: str, args: dict[str, Any]) -> PolicyDecision:
    """The default, harness-owned policy table."""
    if tool in READ_TOOLS:
        return PolicyDecision(Decision.ALLOW)
    if tool in DELETE_TOOLS:
        if not args.get("reason"):
            return PolicyDecision(Decision.DENY, "delete requires a stated reason")
        return PolicyDecision(Decision.ASK, "delete requires human approval")
    if tool in WRITE_TOOLS:
        return PolicyDecision(Decision.ASK, "write requires human approval")
    return PolicyDecision(Decision.ASK, "unknown tool defaults to ask")


def combine(*decisions: PolicyDecision) -> PolicyDecision:
    """Most-restrictive decision wins: deny > ask > allow."""
    return max(decisions, key=lambda decision: _PRECEDENCE[decision.decision])


@dataclass
class AgentPolicy:
    """An agent spec's policy overrides. It can only tighten the harness
    ceiling, never loosen it (e.g. it cannot turn a harness ``ask`` into
    ``allow``)."""

    overrides: dict[str, Decision] = field(default_factory=dict)

    def tighten(self, tool: str, decision: Decision, harness_decision: Decision) -> None:
        if _PRECEDENCE[decision] < _PRECEDENCE[harness_decision]:
            raise PermissionError(
                f"agent spec cannot loosen harness policy for {tool}: "
                f"harness requires {harness_decision.value}"
            )
        self.overrides[tool] = decision

    def apply(self, tool: str, base: PolicyDecision) -> PolicyDecision:
        override = self.overrides.get(tool)
        if override is None:
            return base
        return combine(base, PolicyDecision(override))


@dataclass
class StandingApprovals:
    """Session-scoped standing approvals, e.g. "approve price updates under
    10% for this session"."""

    rules: list[Any] = field(default_factory=list)

    def approve_updates_under(self, percent: float) -> None:
        self.rules.append(("update_product", percent))

    def covers(self, tool: str, old_price: float, new_price: float) -> bool:
        if old_price <= 0:
            return False
        change = abs(new_price - old_price) / old_price * 100
        return any(
            rule_tool == tool and change <= limit for rule_tool, limit in self.rules
        )


@dataclass
class AuditEntry:
    tool: str
    args: dict[str, Any]
    result: Any
    approved: bool


@dataclass
class AuditLog:
    """Records every executed write, cross-checked later against the
    simulator's write log for the fabrication check."""

    entries: list[AuditEntry] = field(default_factory=list)

    def record(self, tool: str, args: dict[str, Any], result: Any, approved: bool) -> None:
        self.entries.append(AuditEntry(tool, args, result, approved))

    @property
    def unapproved_writes(self) -> int:
        return sum(1 for entry in self.entries if not entry.approved)

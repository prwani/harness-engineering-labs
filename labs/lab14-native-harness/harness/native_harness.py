"""Comparison scorecard schema plus mappings from our harness layers to
Claude Code and Copilot CLI concepts (§0.2 of the outline).

This lab doesn't rebuild the harness again; it gives the harness a
vocabulary for describing itself against native, vendor-shipped harnesses,
so `harness compare --native` can print an apples-to-apples table.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ScorecardEntry:
    harness_tag: str  # e.g. "h6"
    accuracy: float
    hallucinations: int
    unapproved_writes: int
    fabricated_claims: int


@dataclass
class ComparisonScorecard:
    """Schema for comparing our harness's progression against native runs."""

    entries: dict[str, ScorecardEntry] = field(default_factory=dict)

    def add(self, entry: ScorecardEntry) -> None:
        self.entries[entry.harness_tag] = entry

    def delta(self, tag: str, baseline_tag: str) -> dict[str, float]:
        current = self.entries[tag]
        baseline = self.entries[baseline_tag]
        return {
            "accuracy": current.accuracy - baseline.accuracy,
            "hallucinations": current.hallucinations - baseline.hallucinations,
            "unapproved_writes": current.unapproved_writes - baseline.unapproved_writes,
            "fabricated_claims": current.fabricated_claims - baseline.fabricated_claims,
        }


# Our layer -> (Claude Code concept, Copilot CLI concept). Reference-only
# mapping data, not executable behaviour (see outline §0.2).
LAYER_MAPPING: dict[str, dict[str, str]] = {
    "harness": {
        "claude_code": "Claude Code runtime via query() / ClaudeSDKClient",
        "copilot_cli": "Copilot CLI itself",
    },
    "agent_spec": {
        "claude_code": "AgentDefinition, .claude/agents/*.md, CLAUDE.md",
        "copilot_cli": "Custom agents (*.agent.md)",
    },
    "custom_tools": {
        "claude_code": "@tool + create_sdk_mcp_server, external MCP",
        "copilot_cli": "MCP servers, function tools",
    },
    "skills_memory": {
        "claude_code": "skills, CLAUDE.md",
        "copilot_cli": "skills, memory files",
    },
    "approval_policy": {
        "claude_code": "can_use_tool, permission modes, PreToolUse hook",
        "copilot_cli": "tool approval",
    },
    "hooks": {
        "claude_code": "PreToolUse, PostToolUse, UserPromptSubmit, Stop, SubagentStop, PreCompact",
        "copilot_cli": "middleware-equivalent hook points",
    },
    "state_compaction": {
        "claude_code": "session resume, auto-compaction",
        "copilot_cli": "session persistence, compaction",
    },
    "orchestration": {
        "claude_code": "sub-agents (agents={}), dynamic workflows",
        "copilot_cli": "sub-agents / fleets",
    },
}


def mapping_for(layer: str) -> dict[str, str]:
    if layer not in LAYER_MAPPING:
        raise KeyError(f"no native-harness mapping for layer: {layer}")
    return LAYER_MAPPING[layer]


def claude_code_mapping() -> dict[str, str]:
    return {layer: mapping["claude_code"] for layer, mapping in LAYER_MAPPING.items()}


def copilot_cli_mapping() -> dict[str, str]:
    return {layer: mapping["copilot_cli"] for layer, mapping in LAYER_MAPPING.items()}


def render_comparison(scorecard: ComparisonScorecard) -> list[dict[str, Any]]:
    """Render the scorecard as rows suitable for `harness compare --native`."""
    return [
        {
            "harness_tag": entry.harness_tag,
            "accuracy": entry.accuracy,
            "hallucinations": entry.hallucinations,
            "unapproved_writes": entry.unapproved_writes,
            "fabricated_claims": entry.fabricated_claims,
        }
        for entry in sorted(scorecard.entries.values(), key=lambda e: e.harness_tag)
    ]

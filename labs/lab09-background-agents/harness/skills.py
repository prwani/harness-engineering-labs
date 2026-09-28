"""Skill registry, skill approval state, tool discovery metadata and MCP
tool namespacing.

Skills are markdown files with frontmatter (name, description, allowed
tools) loaded from a ``skills/`` directory. Each skill has an approval state
so a human can review a skill before an agent may load it. Tool discovery
metadata lets the harness describe registered tools without exposing them
to a spec that didn't ask for them. MCP tools are namespaced by server so
names never collide with local tools.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import re


class SkillApprovalError(Exception):
    """Raised when an unapproved skill is loaded for use."""


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    tools: tuple[str, ...]
    body: str
    approved: bool = False


_FRONTMATTER = re.compile(r"^---\n(?P<meta>.*?)\n---\n(?P<body>.*)$", re.DOTALL)


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = _FRONTMATTER.match(text)
    if not match:
        raise ValueError("skill file is missing frontmatter")
    meta: dict[str, str] = {}
    for line in match.group("meta").splitlines():
        if not line.strip():
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta, match.group("body").strip()


def load_skill(path: Path) -> Skill:
    meta, body = _parse_frontmatter(path.read_text())
    tools = tuple(t.strip() for t in meta.get("tools", "").split(",") if t.strip())
    return Skill(name=meta["name"], description=meta.get("description", ""), tools=tools, body=body)


@dataclass
class SkillRegistry:
    """Loads skills from a directory and tracks their approval state."""

    skills: dict[str, Skill] = field(default_factory=dict)

    def load_dir(self, root: Path) -> None:
        for path in sorted(root.glob("*.md")):
            skill = load_skill(path)
            self.skills[skill.name] = skill

    def approve(self, name: str) -> None:
        skill = self.skills[name]
        self.skills[name] = Skill(skill.name, skill.description, skill.tools, skill.body, approved=True)

    def get(self, name: str) -> Skill:
        skill = self.skills[name]
        if not skill.approved:
            raise SkillApprovalError(f"skill not approved: {name}")
        return skill


@dataclass(frozen=True)
class ToolInfo:
    name: str
    description: str
    namespace: str = "local"


@dataclass
class ToolCatalog:
    """Tool discovery metadata: what's registered, independent of what any
    one agent spec is allowed to use."""

    tools: dict[str, ToolInfo] = field(default_factory=dict)

    def register(self, name: str, description: str, namespace: str = "local") -> None:
        self.tools[name] = ToolInfo(name=name, description=description, namespace=namespace)

    def discover(self, namespace: str | None = None) -> list[ToolInfo]:
        values = list(self.tools.values())
        if namespace is None:
            return values
        return [tool for tool in values if tool.namespace == namespace]


def mcp_namespace(server: str, tool_name: str) -> str:
    """Namespace an MCP tool name so it can never collide with a local tool."""
    return f"mcp:{server}:{tool_name}"


def register_mcp_tools(catalog: ToolCatalog, server: str, tools: list[dict[str, Any]]) -> None:
    for tool in tools:
        namespaced = mcp_namespace(server, tool["name"])
        catalog.register(namespaced, tool.get("description", ""), namespace=f"mcp:{server}")

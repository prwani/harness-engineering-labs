"""Subagents for `harness ask`: delegate a task to a fresh context.

A subagent is defined in ``.harness/agents/<name>.md`` (project) or
``$HARNESS_HOME/agents/<name>.md`` (user): front matter with ``name``,
``description`` and ``tools`` (comma-separated harness tool names; globs
such as ``mcp__orders__*`` are allowed), and a Markdown body that becomes
its system prompt.

The main agent delegates with the ``run_agent`` tool. The subagent starts
with an empty history, its own system prompt and only its tools (they are
the only ones offered, and a ``pre_tool`` policy denies any other). It
shares the project's hooks, permissions, memory, client and trace, so its
calls are governed and counted like any other. Its transcript is saved
next to the parent session, and only its final answer returns to the main
conversation. Subagents cannot start subagents.

Calls run in order. When the model requests two ``run_agent`` calls in one
turn, the harness runs them one after another, so approval prompts never
interleave; each still gets its own context.
"""

from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path
import re
from typing import Any

from harness.hooks import ToolDecision
from harness.session import harness_home

_FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)
_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")


@dataclass(frozen=True)
class AgentDefinition:
    name: str
    description: str
    tools: tuple[str, ...]
    prompt: str
    path: Path
    scope: str

    def allows(self, tool: str) -> bool:
        return any(fnmatchcase(tool, pattern) for pattern in self.tools)


def parse_agent(path: Path, scope: str) -> AgentDefinition:
    match = _FRONT_MATTER.match(path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"{path}: an agent file needs front matter between --- lines")
    meta = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        if key.strip():
            meta[key.strip()] = value.strip()
    name = meta.get("name") or path.stem
    if not _NAME.match(name):
        raise ValueError(f"{path}: agent name must be lowercase letters, digits and hyphens")
    tools = tuple(item.strip() for item in meta.get("tools", "").split(",") if item.strip())
    if not tools:
        raise ValueError(f"{path}: list the agent's tools, e.g. 'tools: list_files, read_file'")
    if any(fnmatchcase("run_agent", pattern) for pattern in tools):
        raise ValueError(f"{path}: subagents cannot run other agents")
    return AgentDefinition(name, meta.get("description", ""), tools, match.group(2).strip(), path, scope)


def discover_agents(repo: Path) -> dict[str, AgentDefinition]:
    """User agents first, so a project agent with the same name replaces it."""
    agents: dict[str, AgentDefinition] = {}
    for scope, root in (("user", harness_home() / "agents"), ("project", repo / ".harness" / "agents")):
        for path in sorted(root.glob("*.md")):
            agent = parse_agent(path, scope)
            agents[agent.name] = agent
    return agents


def agent_tool_policy(agent: AgentDefinition):
    """pre_tool policy: a subagent may only call the tools it lists."""

    def policy(name: str, args: dict[str, Any]) -> ToolDecision:
        if agent.allows(name):
            return ToolDecision(True)
        return ToolDecision(False, f"agent {agent.name} may not use {name}; its tools are {', '.join(agent.tools)}")

    return policy


def agents_prompt(agents: dict[str, AgentDefinition]) -> str:
    if not agents:
        return ""
    lines = ["Subagents can take a self-contained task in a fresh context and return a summary. "
             "Use run_agent when a task matches an agent's description, give it a complete "
             "task description (it cannot see this conversation), and check its summary."]
    lines += [f"- {agent.name}: {agent.description}" for agent in agents.values()]
    return "\n".join(lines)


def agent_tool_definition(agents: dict[str, AgentDefinition]) -> dict[str, Any]:
    return {
        "name": "run_agent",
        "description": "Run a subagent on a task in a fresh context; returns its final answer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent": {"type": "string", "enum": sorted(agents)},
                "task": {"type": "string", "description": "Everything the agent needs to know."},
            },
            "required": ["agent", "task"],
            "additionalProperties": False,
        },
    }


def describe_agents(agents: dict[str, AgentDefinition]) -> str:
    if not agents:
        return "No subagents. Add .harness/agents/<name>.md."
    return "\n".join(f"{agent.name}  [{agent.scope}] tools: {', '.join(agent.tools)}\n    {agent.description}"
                     for agent in agents.values())


SUBAGENT_NOTES = (
    "You are a subagent working in the selected working directory. Hooks and permissions "
    "enforce policy; a denied call did not run, so do not work around it. You cannot ask "
    "the user questions. Finish with a concise summary of what you found or changed, "
    "with evidence, because only that summary is returned."
)

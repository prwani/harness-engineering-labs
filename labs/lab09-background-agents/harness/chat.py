"""One conversation with the harness: a saved session plus per-question settings.

The CLI renders; this class decides what each question runs with. Every
question goes through the same hooked tool loop as Lab 2B, with the
session's history, and each new message is saved as it happens.
"""

from collections.abc import Callable
from dataclasses import dataclass, fields
from pathlib import Path
from time import perf_counter
from typing import Any

from harness.learner import ask_with_tools
from harness.models.adapters import ModelClient, Turn
from harness.agents import AgentDefinition, agent_tool_definition, agents_prompt, discover_agents
from harness.approval import Decision
from harness.mcp_client import MCPServer, mcp_tools, start_servers
from harness.permissions import Approver, PermissionEvent, PermissionRule, Permissions, load_rules
from harness.project_skills import ProjectSkill, discover_skills, skill_text, skill_tool, skills_prompt
from harness.plan_mode import load_todos, save_todos
from harness.session import Session
from harness.todos import TodoList
from harness.tool_loop import LoopStats
from harness.tracing import Meter, MeteredClient, TraceWriter, chain, scrub, trace_results, traced_events


@dataclass
class Events:
    """Optional callbacks the CLI uses to show progress."""

    on_tool_call: Callable[[str, dict[str, Any]], None] | None = None
    on_hook_denial: Callable[[str, str], None] | None = None
    on_hook_feedback: Callable[[str, str], None] | None = None
    on_model_call: Callable[[int], None] | None = None
    approver: Approver | None = None
    on_permission: PermissionEvent | None = None

    def as_kwargs(self) -> dict[str, Any]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


def _prefixed(events: Events, agent: str) -> dict[str, Any]:
    """The parent's events, with each tool name shown as agent:tool."""
    kwargs = events.as_kwargs()
    for name in ("on_tool_call", "on_hook_denial", "on_hook_feedback", "approver", "on_permission"):
        if callback := kwargs.get(name):
            kwargs[name] = lambda tool, *rest, callback=callback: callback(f"{agent}:{tool}", *rest)
    return kwargs


APPROVED = "The plan is approved. Implement it now and keep the todo list up to date."


class Chat:
    def __init__(self, client: ModelClient, repo: Path, session: Session,
                 *, mode: str = "execute", accept_edits: bool = False,
                 trace_path: Path | None = None,
                 on_mcp_error: Callable[[str, Exception], None] | None = None) -> None:
        self.repo, self.session = repo, session
        # Every model call is measured; with a trace path every step is also recorded.
        self.meter = Meter()
        self.trace = TraceWriter(trace_path, session.session_id) if trace_path else None
        self.client = MeteredClient(client, self.meter, self.trace)
        self.set_mode(mode)
        self.permissions = Permissions.load(repo, accept_edits=accept_edits)
        # Todos are harness state, saved next to the session file.
        self.todos_path = session.path.with_suffix(".todos.json") if session.path else None
        self.todos = load_todos(self.todos_path) if self.todos_path else TodoList()
        self.skills: dict[str, ProjectSkill] = discover_skills(repo)
        self.agents: dict[str, AgentDefinition] = discover_agents(repo)
        self.agent_runs = 0
        self.servers: list[MCPServer] = start_servers(repo, on_mcp_error)

    def close(self) -> None:
        for server in self.servers:
            server.close()

    def grant_skill(self, skill: ProjectSkill) -> None:
        """Pre-approve a skill's allowed-tools for the rest of the session."""
        source = f"skill {skill.name}"
        if any(rule.source == source for rule in self.permissions.granted):
            return
        self.permissions.granted += [PermissionRule.parse(text, Decision.ALLOW, source)
                                     for text in skill.allowed_tools]

    def skill_prompt(self, name: str, extra: str = "") -> str:
        """The human invoked /<name>: load the skill directly, no discovery needed."""
        skill = self.skills[name]
        self.grant_skill(skill)
        return f"Use this skill now.\n\n{skill_text(skill)}\n\n{extra}".strip()

    def set_mode(self, mode: str) -> None:
        """Only the human (through the CLI) calls this; no tool can."""
        if mode not in {"plan", "execute"}:
            raise ValueError(f"unknown mode: {mode}")
        self.mode = mode

    def _save_todos(self, todos: TodoList) -> None:
        if self.todos_path:
            save_todos(todos, self.todos_path)

    def ask(self, question: str, events: Events | None = None,
            stats: LoopStats | None = None) -> Turn:
        events = events or Events()
        stats = stats if stats is not None else LoopStats()
        on_message = self.session.save
        if self.trace:
            events = traced_events(events, self.trace)
            on_message = chain(self.session.save, trace_results(self.trace))
            self.trace.write("run_start", question=scrub(question), mode=self.mode, repo=str(self.repo))
        # Settings and skills are reread for every question; session approvals are kept.
        self.permissions.rules = load_rules(self.repo)
        self.skills = discover_skills(self.repo)
        self.agents = discover_agents(self.repo)
        tools, definitions = mcp_tools(self.servers)
        agent_tools, agent_definitions = dict(tools), list(definitions)
        if self.skills:
            tools["use_skill"], definition = skill_tool(self.skills, self.grant_skill)
            definitions.append(definition)
        if self.agents:
            tools["run_agent"] = self._agent_runner(events, agent_tools, agent_definitions)
            definitions.append(agent_tool_definition(self.agents))
        started, error = perf_counter(), None
        try:
            return ask_with_tools(
                self.client,
                question,
                repo=self.repo,
                stats=stats,
                history=self.session.messages,
                on_message=on_message,
                mode=self.mode,
                todos=self.todos,
                on_todos=self._save_todos,
                permissions=self.permissions,
                extra_tools=tools,
                extra_definitions=definitions,
                extra_prompt="\n\n".join(part for part in (skills_prompt(self.skills),
                                                             agents_prompt(self.agents)) if part),
                **events.as_kwargs(),
            )
        except Exception as caught:
            error = scrub(str(caught))
            raise
        finally:
            if self.trace:
                self.trace.write(
                    "run_end", seconds=round(perf_counter() - started, 3), llm_calls=stats.model_calls,
                    tool_calls=stats.tool_calls, denied=stats.denied_calls,
                    tool_errors=stats.tool_errors, error=error,
                )

    def _agent_runner(self, events: Events, tools: dict[str, Any],
                      definitions: list[dict[str, Any]]) -> Callable[[dict[str, Any]], str]:
        """The run_agent tool: a fresh history, the agent's prompt and tools, shared governance."""

        def run_agent(args: dict[str, Any]) -> str:
            agent = self.agents.get(str(args.get("agent", "")))
            if agent is None:
                raise ValueError(f"unknown agent {args.get('agent')!r}; available: {', '.join(self.agents)}")
            self.agent_runs += 1
            path = None
            if self.session.path:
                path = (self.session.path.parent / f"{self.session.session_id}.agents"
                        / f"{self.agent_runs:02d}-{agent.name}.jsonl")
            child, stats = Session(path=path, name=f"agent:{agent.name}"), LoopStats()
            turn = ask_with_tools(
                self.client, str(args.get("task", "")), repo=self.repo, stats=stats,
                history=child.messages, on_message=child.save if path else None,
                permissions=self.permissions, extra_tools=tools, extra_definitions=definitions,
                agent=agent, **_prefixed(events, agent.name),
            )
            where = f"; transcript {path}" if path else ""
            return (f"Agent {agent.name} finished ({stats.model_calls} LLM calls, "
                    f"{stats.tool_calls} tool calls, {stats.denied_calls} denied{where}):\n{turn.text}")

        return run_agent

    def questions(self) -> list[str]:
        return [message["content"] for message in self.session.messages
                if message["role"] == "user" and isinstance(message["content"], str)]

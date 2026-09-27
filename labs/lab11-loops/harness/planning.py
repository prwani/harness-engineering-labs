"""Planner and executor agent specs, and the mode switch the harness owns.

Two modes are two agent specs on one harness: ``planner`` only has read
tools plus ``write_todos``; ``executor`` has the write tools and works
through the open todos. Only the harness may switch between them; an agent
cannot promote itself from planner to executor.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentSpec:
    name: str
    tools: tuple[str, ...]
    model: str = "claude"


PLANNER = AgentSpec(name="planner", tools=("list_products", "get_product", "write_todos"))
EXECUTOR = AgentSpec(
    name="catalog-fixer",
    tools=("list_products", "get_product", "update_product", "create_product", "delete_product"),
)

WRITE_TOOLS = {"update_product", "create_product", "delete_product"}


@dataclass
class ModeSwitch:
    """The single place allowed to change which agent spec is active."""

    _mode: str = "plan"
    _specs: dict[str, AgentSpec] = field(
        default_factory=lambda: {"plan": PLANNER, "execute": EXECUTOR}
    )

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def spec(self) -> AgentSpec:
        return self._specs[self._mode]

    def switch(self, mode: str) -> AgentSpec:
        if mode not in self._specs:
            raise ValueError(f"unknown mode: {mode}")
        self._mode = mode
        return self.spec


def has_write_tools(spec: AgentSpec) -> bool:
    return any(tool in WRITE_TOOLS for tool in spec.tools)

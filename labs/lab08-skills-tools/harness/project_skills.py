"""Project skills for `harness ask`: packaged procedures loaded on demand.

A skill is a folder with a ``SKILL.md``: front matter (``name``,
``description``, optional ``allowed-tools``) and a Markdown body with the
procedure. Skills are found in ``.harness/skills/<name>/SKILL.md`` in the
project and ``$HARNESS_HOME/skills/<name>/SKILL.md`` for the user; a project
skill wins over a user skill with the same name.

Only each skill's name and description go in the system prompt. The body is
loaded when it's used: by the model through the ``use_skill`` tool when the
description matches the task, or by the human with ``/<skill-name>``.

``allowed-tools`` lists permission rules (Lab 6 syntax, separated by spaces)
that are pre-approved once the skill is in use, so its routine steps run
without prompts. They never override a deny or an explicit ask rule.
"""

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from harness.session import harness_home

_FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)
_RULE_TOKEN = re.compile(r"[A-Za-z0-9_*?\[\]-]+(?:\([^)]*\))?")
_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")


@dataclass(frozen=True)
class ProjectSkill:
    name: str
    description: str
    allowed_tools: tuple[str, ...]
    body: str
    path: Path
    scope: str


def parse_skill(path: Path, scope: str) -> ProjectSkill:
    text = path.read_text(encoding="utf-8")
    match = _FRONT_MATTER.match(text)
    if not match:
        raise ValueError(f"{path}: SKILL.md needs front matter between --- lines")
    meta = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        if key.strip():
            meta[key.strip()] = value.strip()
    name = meta.get("name") or path.parent.name
    if not _NAME.match(name):
        raise ValueError(f"{path}: skill name must be lowercase letters, digits and hyphens")
    if not meta.get("description"):
        raise ValueError(f"{path}: a skill needs a description; it is how the model finds it")
    return ProjectSkill(
        name=name,
        description=meta["description"],
        allowed_tools=tuple(_RULE_TOKEN.findall(meta.get("allowed-tools", ""))),
        body=match.group(2).strip(),
        path=path,
        scope=scope,
    )


def discover_skills(repo: Path) -> dict[str, ProjectSkill]:
    """User skills first, so a project skill with the same name replaces it."""
    skills: dict[str, ProjectSkill] = {}
    for scope, root in (("user", harness_home() / "skills"), ("project", repo / ".harness" / "skills")):
        for path in sorted(root.glob("*/SKILL.md")):
            skill = parse_skill(path, scope)
            skills[skill.name] = skill
    return skills


def skills_prompt(skills: dict[str, ProjectSkill]) -> str:
    if not skills:
        return ""
    lines = ["Skills are procedures for specific tasks. When a task matches a skill's "
             "description, call use_skill with its name first, then follow it."]
    lines += [f"- {skill.name}: {skill.description}" for skill in skills.values()]
    return "\n".join(lines)


def skill_text(skill: ProjectSkill) -> str:
    return f"Skill {skill.name} ({skill.path.parent}):\n\n{skill.body}"


def skill_tool(skills: dict[str, ProjectSkill], on_use=None):
    """The ``use_skill`` tool and its definition."""

    def use_skill(args: dict[str, Any]) -> str:
        skill = skills.get(str(args.get("name", "")))
        if skill is None:
            raise ValueError(f"unknown skill {args.get('name')!r}; available: {', '.join(skills) or 'none'}")
        if on_use:
            on_use(skill)
        return skill_text(skill)

    definition = {
        "name": "use_skill",
        "description": "Load a skill's full instructions by name. Skills are listed in the system prompt.",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string", "enum": sorted(skills)}},
            "required": ["name"],
            "additionalProperties": False,
        },
    }
    return use_skill, definition


def describe_skills(skills: dict[str, ProjectSkill]) -> str:
    if not skills:
        return "No skills. Add .harness/skills/<name>/SKILL.md."
    return "\n".join(
        f"/{skill.name}  [{skill.scope}] {skill.description}"
        + (f"\n    allowed-tools: {' '.join(skill.allowed_tools)}" if skill.allowed_tools else "")
        for skill in skills.values()
    )

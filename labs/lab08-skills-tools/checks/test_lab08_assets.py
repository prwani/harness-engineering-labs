from pathlib import Path

from harness.project_skills import parse_skill

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def test_release_notes_skill_parses():
    skill = parse_skill(ASSETS / ".harness" / "skills" / "release-notes" / "SKILL.md", "project")
    assert skill.name == "release-notes"
    assert "git_cli(log *)" in skill.allowed_tools
    assert "edit_file(CHANGELOG.md)" in skill.allowed_tools
    assert "Do not commit" in skill.body

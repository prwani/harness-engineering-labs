import pytest

from harness.skills import (
    SkillApprovalError,
    SkillRegistry,
    ToolCatalog,
    load_skill,
    mcp_namespace,
    register_mcp_tools,
)


def test_load_skill_parses_frontmatter(tmp_path):
    path = tmp_path / "product-description.md"
    path.write_text(
        "---\nname: product-description\ndescription: Write catalog copy\ntools: get_product, update_product\n---\nBody text.\n"
    )

    skill = load_skill(path)

    assert skill.name == "product-description"
    assert skill.tools == ("get_product", "update_product")
    assert skill.body == "Body text."
    assert not skill.approved


def test_registry_denies_unapproved_skills(tmp_path):
    path = tmp_path / "s.md"
    path.write_text("---\nname: s\ndescription: d\ntools:\n---\nbody\n")
    registry = SkillRegistry()
    registry.load_dir(tmp_path)

    with pytest.raises(SkillApprovalError):
        registry.get("s")


def test_registry_allows_approved_skills(tmp_path):
    path = tmp_path / "s.md"
    path.write_text("---\nname: s\ndescription: d\ntools:\n---\nbody\n")
    registry = SkillRegistry()
    registry.load_dir(tmp_path)

    registry.approve("s")

    assert registry.get("s").approved


def test_tool_catalog_supports_discovery_by_namespace():
    catalog = ToolCatalog()
    catalog.register("get_product", "fetch a product")

    register_mcp_tools(catalog, "filesystem", [{"name": "read_file", "description": "read a file"}])

    all_tools = {tool.name for tool in catalog.discover()}
    mcp_tools = catalog.discover(namespace="mcp:filesystem")

    assert "get_product" in all_tools
    assert mcp_namespace("filesystem", "read_file") in all_tools
    assert len(mcp_tools) == 1
    assert mcp_tools[0].namespace == "mcp:filesystem"


def test_mcp_namespace_never_collides_with_local_tools():
    catalog = ToolCatalog()
    catalog.register("read_file", "local sandboxed reader")

    register_mcp_tools(catalog, "filesystem", [{"name": "read_file", "description": "remote reader"}])

    assert catalog.tools["read_file"].namespace == "local"
    assert catalog.tools[mcp_namespace("filesystem", "read_file")].namespace == "mcp:filesystem"

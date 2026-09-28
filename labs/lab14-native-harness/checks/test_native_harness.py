import pytest

from harness.native_harness import (
    ComparisonScorecard,
    ScorecardEntry,
    claude_code_mapping,
    copilot_cli_mapping,
    mapping_for,
    render_comparison,
)


def test_scorecard_computes_delta_between_tags():
    scorecard = ComparisonScorecard()
    scorecard.add(ScorecardEntry("h4", accuracy=0.5, hallucinations=3, unapproved_writes=2, fabricated_claims=1))
    scorecard.add(ScorecardEntry("h6", accuracy=0.9, hallucinations=0, unapproved_writes=0, fabricated_claims=0))

    delta = scorecard.delta("h6", baseline_tag="h4")

    assert delta["accuracy"] == pytest.approx(0.4)
    assert delta["unapproved_writes"] == -2


def test_render_comparison_sorts_by_tag():
    scorecard = ComparisonScorecard()
    scorecard.add(ScorecardEntry("h6", accuracy=0.9, hallucinations=0, unapproved_writes=0, fabricated_claims=0))
    scorecard.add(ScorecardEntry("h4", accuracy=0.5, hallucinations=3, unapproved_writes=2, fabricated_claims=1))

    rows = render_comparison(scorecard)

    assert [row["harness_tag"] for row in rows] == ["h4", "h6"]


def test_claude_code_mapping_covers_every_layer():
    mapping = claude_code_mapping()

    assert mapping["harness"] == "Claude Code runtime via query() / ClaudeSDKClient"
    assert "approval_policy" in mapping


def test_copilot_cli_mapping_covers_every_layer():
    mapping = copilot_cli_mapping()

    assert mapping["harness"] == "Copilot CLI itself"
    assert set(mapping) == set(claude_code_mapping())


def test_mapping_for_unknown_layer_raises():
    with pytest.raises(KeyError):
        mapping_for("nonexistent-layer")

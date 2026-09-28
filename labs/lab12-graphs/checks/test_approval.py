import pytest

from harness.approval import (
    AgentPolicy,
    AuditLog,
    Decision,
    PolicyDecision,
    StandingApprovals,
    combine,
    harness_policy,
)


def test_reads_are_auto_approved():
    assert harness_policy("list_products", {}).decision == Decision.ALLOW
    assert harness_policy("get_product", {"id": "1"}).decision == Decision.ALLOW


def test_update_and_create_require_a_human():
    assert harness_policy("update_product", {}).decision == Decision.ASK
    assert harness_policy("create_product", {}).decision == Decision.ASK


def test_delete_without_reason_is_denied():
    decision = harness_policy("delete_product", {"id": "1"})

    assert decision.decision == Decision.DENY
    assert "reason" in decision.reason


def test_delete_with_reason_asks_a_human():
    decision = harness_policy("delete_product", {"id": "1", "reason": "duplicate SKU"})

    assert decision.decision == Decision.ASK


def test_deny_wins_over_allow_for_the_same_call():
    combined = combine(PolicyDecision(Decision.ALLOW), PolicyDecision(Decision.DENY))

    assert combined.decision == Decision.DENY


def test_agent_spec_cannot_loosen_harness_policy():
    policy = AgentPolicy()

    with pytest.raises(PermissionError):
        policy.tighten("delete_product", Decision.ALLOW, harness_decision=Decision.ASK)


def test_agent_spec_can_tighten_harness_policy():
    policy = AgentPolicy()
    policy.tighten("update_product", Decision.DENY, harness_decision=Decision.ASK)

    result = policy.apply("update_product", PolicyDecision(Decision.ASK))

    assert result.decision == Decision.DENY


def test_standing_approval_covers_small_price_changes():
    standing = StandingApprovals()
    standing.approve_updates_under(10)

    assert standing.covers("update_product", old_price=100, new_price=105)
    assert not standing.covers("update_product", old_price=100, new_price=150)


def test_audit_log_tracks_unapproved_writes():
    log = AuditLog()
    log.record("update_product", {"id": "1"}, {"status": "ok"}, approved=True)
    log.record("delete_product", {"id": "2"}, {"status": "ok"}, approved=False)

    assert log.unapproved_writes == 1
    assert len(log.entries) == 2

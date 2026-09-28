"""Idempotent write execution and crash-safe reconciliation.

Every write carries an idempotency key. Mutating calls run one at a time.
On resume, a write with no persisted result is reconciled against the
simulator's write log by its key: if it was applied, the logged result is
reused; if not, the call is re-run. This extends the Lab 3 crash rule to
mutating tools.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
import hashlib
import json


def idempotency_key(tool: str, args: dict[str, Any]) -> str:
    payload = json.dumps({"tool": tool, "args": args}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


@dataclass
class WriteLog:
    """Records every write the simulator actually applied, keyed by its
    idempotency key, so a resumed run can reconcile instead of re-executing."""

    entries: dict[str, Any] = field(default_factory=dict)

    def record(self, key: str, result: Any) -> None:
        self.entries[key] = result

    def applied(self, key: str) -> bool:
        return key in self.entries

    def result_for(self, key: str) -> Any:
        return self.entries[key]


def run_write(
    tool: Callable[[dict[str, Any]], Any],
    name: str,
    args: dict[str, Any],
    log: WriteLog,
) -> tuple[str, Any]:
    """Run (or reconcile) one mutating call and return its (key, result)."""
    key = idempotency_key(name, args)
    if log.applied(key):
        return key, log.result_for(key)
    result = tool(args)
    log.record(key, result)
    return key, result

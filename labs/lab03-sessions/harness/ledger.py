"""Provider-reported usage ledger."""

from dataclasses import asdict, dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    cache_write_tokens: int = 0


class Ledger:
    def __init__(self) -> None:
        self.entries: list[Usage] = []

    def record(self, usage: Usage) -> None:
        self.entries.append(usage)

    def totals(self) -> Usage:
        return Usage(**{
            field: sum(getattr(entry, field) for entry in self.entries)
            for field in Usage.__dataclass_fields__
        })

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps([asdict(entry) for entry in self.entries], indent=2))

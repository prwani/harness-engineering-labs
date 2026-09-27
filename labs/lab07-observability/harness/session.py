"""JSONL-backed session history for Lab 3."""

from dataclasses import asdict, dataclass, field
from pathlib import Path
import json
from uuid import uuid4


@dataclass
class Session:
    session_id: str = field(default_factory=lambda: uuid4().hex)
    messages: list[dict] = field(default_factory=list)

    def append(self, message: dict, path: Path) -> None:
        self.messages.append(message)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as file:
            file.write(json.dumps({"session_id": self.session_id, "message": message}) + "\n")

    @classmethod
    def resume(cls, path: Path) -> "Session":
        entries = [json.loads(line) for line in path.read_text().splitlines()]
        if not entries:
            raise ValueError("cannot resume an empty session")
        session_id = entries[0]["session_id"]
        if any(entry["session_id"] != session_id for entry in entries):
            raise ValueError("session file contains multiple session IDs")
        return cls(session_id=session_id, messages=[entry["message"] for entry in entries])

"""JSONL-backed sessions: persisted conversations you can continue, resume and fork.

A session is the conversation (questions, model turns, tool calls and their
results), appended to a JSONL file after every step. It is not a snapshot of
the repository: files can change while a session is paused.

Sessions live outside the project, under ``$HARNESS_HOME/projects/<project>/``
(default ``~/.harness``), the way Claude Code keeps them under ``~/.claude``.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from typing import Any
from uuid import uuid4


def harness_home() -> Path:
    """Root for per-user harness state; override with HARNESS_HOME."""
    return Path(os.environ.get("HARNESS_HOME") or Path.home() / ".harness")


def project_dir(repo: Path) -> Path:
    """Per-project state folder, keyed by the project's absolute path."""
    key = re.sub(r"[^A-Za-z0-9]+", "-", str(repo.resolve())).strip("-") or "root"
    return harness_home() / "projects" / key


def to_jsonable(value: Any) -> Any:
    """Convert provider SDK objects (content blocks, output items) to plain JSON."""
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", exclude_none=True)
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    return value


def repair_history(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Pair tool calls that never got a persisted result (a crash mid-call).

    The interrupted call is not silently dropped or re-run: the model gets an
    explicit result saying it was interrupted, and decides what to do next.
    """
    if messages and messages[-1].get("role") == "assistant" and messages[-1].get("call_ids"):
        messages.append({
            "role": "tool",
            "content": [
                {"call_id": call_id,
                 "output": "ERROR: interrupted before a result was saved; check the "
                           "current state and run it again if it is still needed."}
                for call_id in messages[-1]["call_ids"]
            ],
        })
    return messages


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Session:
    session_id: str = field(default_factory=lambda: uuid4().hex)
    messages: list[dict] = field(default_factory=list)
    name: str | None = None
    forked_from: str | None = None
    path: Path | None = None

    def append(self, message: dict, path: Path) -> None:
        self.messages.append(message)
        self._write(message, path)

    def save(self, message: dict) -> None:
        """Persist a message that is already in ``messages`` (the loop appends it)."""
        if self.path is None:
            raise ValueError("session has no file")
        self._write(message, self.path)

    def replace(self, messages: list[dict]) -> None:
        """Swap the history (after /compact or /clear); the file keeps the old part.

        A ``reset`` entry marks the point where a resumed session starts again.
        """
        self.messages[:] = messages
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as file:
                file.write(json.dumps({"session_id": self.session_id, "reset": True}) + "\n")
            for message in messages:
                self._write(message, self.path)

    def _write(self, message: dict, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = {"session_id": self.session_id, "message": to_jsonable(message)}
        with path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry) + "\n")

    @classmethod
    def resume(cls, path: Path) -> "Session":
        entries = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
        if not entries:
            raise ValueError("cannot resume an empty session")
        session_id = entries[0]["session_id"]
        if any(entry["session_id"] != session_id for entry in entries):
            raise ValueError("session file contains multiple session IDs")
        messages: list[dict] = []
        for entry in entries:
            if entry.get("reset"):
                messages = []
            else:
                messages.append(entry["message"])
        return cls(session_id=session_id, messages=messages, path=path)


@dataclass(frozen=True)
class SessionInfo:
    session_id: str
    name: str | None
    forked_from: str | None
    created: str
    path: Path
    messages: int
    size: int
    title: str


class SessionStore:
    """Create, list, find and fork the sessions of one project."""

    def __init__(self, repo: Path) -> None:
        self.root = project_dir(repo) / "sessions"

    def create(self, name: str | None = None, *, forked_from: str | None = None,
               messages: list[dict] | None = None) -> Session:
        session = Session(name=name, forked_from=forked_from)
        session.path = self.root / f"{session.session_id}.jsonl"
        self.root.mkdir(parents=True, exist_ok=True)
        meta = {"session_id": session.session_id, "name": name,
                "forked_from": forked_from, "created": _now()}
        (self.root / f"{session.session_id}.meta.json").write_text(json.dumps(meta), encoding="utf-8")
        for message in messages or []:
            session.append(message, session.path)
        return session

    def list(self) -> list[SessionInfo]:
        infos = []
        for meta_file in self.root.glob("*.meta.json"):
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
            path = self.root / f"{meta['session_id']}.jsonl"
            lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
            title = ""
            for line in lines:
                message = json.loads(line).get("message", {})
                if message.get("role") == "user" and isinstance(message.get("content"), str):
                    title = message["content"].splitlines()[0][:60]
                    break
            infos.append(SessionInfo(
                meta["session_id"], meta.get("name"), meta.get("forked_from"), meta.get("created", ""),
                path, len(lines), path.stat().st_size if path.exists() else 0, title,
            ))
        return sorted(infos, key=lambda info: info.path.stat().st_mtime if info.path.exists() else 0,
                      reverse=True)

    def latest(self) -> SessionInfo | None:
        sessions = self.list()
        return sessions[0] if sessions else None

    def find(self, ref: str) -> SessionInfo:
        """Match a full ID, a unique ID prefix, or a name (most recent wins)."""
        sessions = self.list()
        for info in sessions:
            if info.session_id == ref:
                return info
        named = [info for info in sessions if info.name == ref]
        if named:
            return named[0]
        prefixed = [info for info in sessions if info.session_id.startswith(ref)]
        if len(prefixed) == 1:
            return prefixed[0]
        if prefixed:
            raise ValueError(f"session prefix {ref!r} is ambiguous")
        raise ValueError(f"no session matches {ref!r}; run `harness sessions` to list them")

    def load(self, info: SessionInfo) -> Session:
        if not info.path.exists():
            return Session(session_id=info.session_id, name=info.name,
                           forked_from=info.forked_from, path=info.path)
        session = Session.resume(info.path)
        session.name, session.forked_from = info.name, info.forked_from
        persisted = len(session.messages)
        for message in repair_history(session.messages)[persisted:]:
            session.save(message)
        return session

    def fork(self, info: SessionInfo, name: str | None = None) -> Session:
        """Copy a conversation into a new session; the original is untouched."""
        return self.create(name or info.name, forked_from=info.session_id,
                           messages=self.load(info).messages)

    def open(self, *, name: str | None = None, continue_latest: bool = False,
             resume: str | None = None, fork: bool = False) -> Session:
        """Start a new session, or continue/resume (and optionally fork) one."""
        if continue_latest and resume:
            raise ValueError("use either --continue or --resume, not both")
        info = None
        if resume:
            info = self.find(resume)
        elif continue_latest:
            info = self.latest()
            if info is None:
                raise ValueError("there is no session to continue in this project")
        if info is None:
            if fork:
                raise ValueError("--fork needs --continue or --resume")
            return self.create(name)
        return self.fork(info, name) if fork else self.load(info)

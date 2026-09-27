"""Session-scoped file memory, shared-store concurrency, and scope enforcement.

Session-scoped ``memory/`` is on by default. A shared, cross-session store is
opt-in and scoped per agent spec (read-only or read-write). It uses
optimistic concurrency: a write fails if the file changed since it was read.
A path outside an agent's granted scopes is denied.
"""

from dataclasses import dataclass, field
from pathlib import Path
import hashlib


class ScopeError(Exception):
    """Raised when a path falls outside an agent's granted scopes."""


class ConcurrencyError(Exception):
    """Raised when a shared file changed since it was last read."""


def _fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


@dataclass
class SessionMemory:
    """Always-on, session-scoped memory (``notes.md``, ``catalog_snapshot.json``)."""

    root: Path

    def write(self, name: str, content: str) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / name
        path.write_text(content)
        return path

    def read(self, name: str) -> str:
        return (self.root / name).read_text()


@dataclass
class SharedStore:
    """Opt-in, cross-session store with optimistic concurrency."""

    root: Path
    mode: str = "ro"  # "ro" or "rw"
    _versions: dict[str, str] = field(default_factory=dict)

    def read(self, name: str) -> tuple[str, str]:
        content = (self.root / name).read_text()
        version = _fingerprint(content)
        self._versions[name] = version
        return content, version

    def write(self, name: str, content: str, if_match: str) -> str:
        if self.mode != "rw":
            raise PermissionError(f"shared store is read-only: {name}")
        path = self.root / name
        current = path.read_text() if path.exists() else ""
        if _fingerprint(current) != if_match:
            raise ConcurrencyError(f"{name} changed since it was read")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        new_version = _fingerprint(content)
        self._versions[name] = new_version
        return new_version


@dataclass(frozen=True)
class FileScope:
    """The scopes an agent spec is granted; enforced by a ``pre_tool`` hook."""

    allowed_roots: tuple[Path, ...]

    def check(self, path: Path) -> Path:
        resolved = path.resolve()
        for root in self.allowed_roots:
            root_resolved = root.resolve()
            if resolved == root_resolved or root_resolved in resolved.parents:
                return resolved
        raise ScopeError(f"path outside granted scopes: {path}")


def snapshot_key(repo_sha: str, sim_state_version: str, task: str) -> str:
    """Cache key for freshness checks on artefacts like ``catalog_snapshot.json``."""
    return _fingerprint(f"{repo_sha}:{sim_state_version}:{task}")


@dataclass
class CachedArtifact:
    key: str
    content: str

    def is_stale(self, current_key: str) -> bool:
        return self.key != current_key

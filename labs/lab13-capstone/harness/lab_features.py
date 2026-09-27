"""Declarative first-cut capability metadata for a lab snapshot."""

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class LabFeatures:
    number: int
    slug: str
    title: str
    capabilities: tuple[str, ...]
    live_validation: tuple[str, ...]


def load_features(root: Path | None = None) -> LabFeatures:
    root = root or Path.cwd()
    data = json.loads((root / "lab.json").read_text())
    return LabFeatures(
        number=data["number"],
        slug=data["slug"],
        title=data["title"],
        capabilities=tuple(data["capabilities"]),
        live_validation=tuple(data["live_validation"]),
    )

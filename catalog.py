"""Read-only catalog construction from Hermes-owned profile files."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re

_DESCRIPTION = re.compile(r"^description:\s*[\"']?(.+?)[\"']?\s*$", re.MULTILINE)


@dataclass(frozen=True)
class Candidate:
    name: str
    description: str
    source: str
    excerpt: str = ""

    def compact(self) -> dict:
        return asdict(self)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return ""


def _description(text: str, fallback: str) -> str:
    match = _DESCRIPTION.search(text)
    return match.group(1).strip() if match else fallback


def profile_catalog(home: Path, excerpt_chars: int = 1200) -> list[Candidate]:
    profiles = home / "profiles"
    if not profiles.is_dir():
        return []
    result = []
    for profile in sorted(p for p in profiles.iterdir() if p.is_dir()):
        soul = _read(profile / "SOUL.md")
        config = _read(profile / "config.yaml")
        result.append(Candidate(profile.name, _description(config, "Hermes profile; inspect SOUL.md for its role."), "profile", soul[:excerpt_chars]))
    return result


def skill_catalog(profile_root: Path, excerpt_chars: int = 700) -> list[Candidate]:
    skills = profile_root / "skills"
    if not skills.is_dir():
        return []
    result = []
    for skill_file in sorted(skills.glob("*/SKILL.md")):
        text = _read(skill_file)
        result.append(Candidate(skill_file.parent.name, _description(text, "Hermes skill."), "skill", text[:excerpt_chars]))
    return result

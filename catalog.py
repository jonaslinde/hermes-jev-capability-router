"""Read-only catalog construction from Hermes-owned profile files."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re

_DESCRIPTION = re.compile(r"^description:\s*[\"']?(.+?)[\"']?\s*$", re.MULTILINE)
_QUERY_ALIASES = {
    "mail": "email", "mejl": "email", "oläst": "unread", "olästa": "unread",
    "läs": "read", "läsa": "read", "summera": "summarize", "sammanfatta": "summarize",
    "åtgärd": "action", "åtgärder": "action",
}
_QUERY_STOPWORDS = {"och", "att", "denna", "den", "det", "jag", "någon", "behöver", "innan", "börjar"}


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


def _terms(text: str, *, query: bool = False) -> set[str]:
    terms = {term.lower() for term in re.findall(r"[A-Za-zÅÄÖåäö0-9_-]{3,}", text)}
    terms |= {part for term in terms for part in re.split(r"[-_]", term) if len(part) >= 3}
    if not query:
        return terms
    terms = {_QUERY_ALIASES.get(term, term) for term in terms if term not in _QUERY_STOPWORDS}
    if "email" in terms:
        terms.add("inbox")
    return terms


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


def skill_catalog(profile_root: Path, excerpt_chars: int = 700, *, request: str = "", limit: int = 40) -> list[Candidate]:
    """Return a compact, relevant candidate set from a profile's active skills.

    Hermes profiles commonly organize skills below topic directories. Hidden
    folders such as ``.archive`` and ``.hub`` are intentionally excluded. A
    deterministic lexical prefilter keeps the Jev request small; Jev remains
    the sole decision-maker among the eligible candidates.
    """
    skills = profile_root / "skills"
    if not skills.is_dir():
        return []
    ranked: list[tuple[int, Candidate]] = []
    request_terms = _terms(request, query=True)
    for skill_file in sorted(skills.rglob("SKILL.md")):
        relative = skill_file.relative_to(skills)
        if any(part.startswith(".") for part in relative.parts):
            continue
        text = _read(skill_file)
        candidate = Candidate(skill_file.parent.name, _description(text, "Hermes skill."), "skill", text[:excerpt_chars])
        score = 5 * len(request_terms & _terms(candidate.name))
        score += len(request_terms & _terms(candidate.description))
        if candidate.name.replace("-", " ") in request.lower():
            score += 2
        ranked.append((score, candidate))
    ranked.sort(key=lambda item: (-item[0], item[1].name))
    return [candidate for _score, candidate in ranked[:max(1, limit)]]

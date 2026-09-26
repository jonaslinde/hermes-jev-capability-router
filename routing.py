"""Typed Jev requests and deterministic confidence gates."""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Protocol
from urllib.request import Request, urlopen

try:  # Hermes loads this as a package; direct tests load it from the repo root.
    from .catalog import Candidate
except ImportError:  # pragma: no cover - exercised by stdlib test discovery
    from catalog import Candidate


class Transport(Protocol):
    def evaluate(self, payload: dict) -> dict: ...


class OpenRouterTransport:
    def __init__(self, endpoint: str, api_key: str, timeout: int = 20):
        self.endpoint, self.api_key, self.timeout = endpoint, api_key, timeout

    def evaluate(self, payload: dict) -> dict:
        request = Request(self.endpoint, data=json.dumps(payload).encode(), headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=self.timeout) as response:
            return json.load(response)


@dataclass(frozen=True)
class Recommendation:
    selected: str | None
    confidence: float
    probabilities: dict[str, float]
    reason: str

    def json(self) -> str:
        return json.dumps(self.__dict__, ensure_ascii=False)


def recommend(transport: Transport, request: str, candidates: list[Candidate], *, model: str, threshold: float, kind: str) -> Recommendation:
    if not candidates:
        return Recommendation(None, 0.0, {}, "no eligible candidates")
    criteria = {c.name: c.description for c in candidates}
    criteria["no_match"] = "No listed candidate is appropriate; do not guess."
    payload = {"model": model, "state": {"request": request, "candidates": [c.compact() for c in candidates]}, "questions": {"route": {"type": "choice", "instructions": f"Choose the single best eligible {kind} for this request. Choose no_match if none fits. This is advisory only.", "criteria": criteria}}}
    try:
        answer = transport.evaluate(payload).get("answers", {}).get("route", {})
        selected = answer.get("choice") or answer.get("selected") or answer.get("value")
        probabilities = answer.get("probabilities") or {}
        confidence = float(answer.get("confidence", max(probabilities.values(), default=0.0)))
    except (OSError, ValueError, TypeError, KeyError):
        return Recommendation(None, 0.0, {}, "Jev unavailable or malformed response")
    if selected == "no_match" or selected not in criteria or confidence < threshold:
        return Recommendation(None, confidence, probabilities, "no match or below confidence threshold")
    return Recommendation(selected, confidence, probabilities, "recommended")


def configured_transport(settings: dict) -> OpenRouterTransport | None:
    key = os.getenv("OPENROUTER_API_KEY")
    return OpenRouterTransport(settings.get("endpoint", "https://openrouter.ai/api/alpha/decisions"), key) if key else None

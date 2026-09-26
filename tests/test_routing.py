import unittest
from types import ModuleType
from unittest.mock import patch

from catalog import Candidate
from routing import configured_transport, recommend


class FakeTransport:
    def __init__(self, answer): self.answer = answer; self.payload = None
    def evaluate(self, payload): self.payload = payload; return self.answer


class RoutingTests(unittest.TestCase):
    def setUp(self): self.candidates = [Candidate("researcher", "Research primary sources", "profile"), Candidate("maintainer", "Maintain Hermes", "profile")]

    def test_returns_confident_candidate(self):
        transport = FakeTransport({"answers": {"route": {"choice": "researcher", "confidence": .91, "probabilities": {"researcher": .91, "maintainer": .04, "no_match": .05}}}})
        result = recommend(transport, "Find source-backed market research", self.candidates, model="typesafe/jev-1.13", threshold=.7, kind="profile")
        self.assertEqual(result.selected, "researcher")
        self.assertIn("no_match", transport.payload["questions"]["route"]["criteria"])

    def test_low_confidence_never_guesses(self):
        transport = FakeTransport({"answers": {"route": {"choice": "researcher", "confidence": .49, "probabilities": {"researcher": .49}}}})
        self.assertIsNone(recommend(transport, "ambiguous", self.candidates, model="m", threshold=.7, kind="profile").selected)

    def test_malformed_response_fails_open(self):
        transport = FakeTransport({"answers": {"route": {"choice": "unknown", "confidence": "bad"}}})
        result = recommend(transport, "anything", self.candidates, model="m", threshold=.7, kind="profile")
        self.assertIsNone(result.selected)
        self.assertIn("unavailable", result.reason)

    def test_empty_catalog(self):
        result = recommend(FakeTransport({}), "anything", [], model="m", threshold=.7, kind="profile")
        self.assertEqual(result.reason, "no eligible candidates")

    def test_uses_hermes_scoped_secret_resolver(self):
        agent = ModuleType("agent")
        secret_scope = ModuleType("agent.secret_scope")
        secret_scope.get_secret = lambda name, default="": "profile-only-key"
        with patch.dict("sys.modules", {"agent": agent, "agent.secret_scope": secret_scope}):
            self.assertIsNotNone(configured_transport({}))

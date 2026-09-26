import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PluginContractTests(unittest.TestCase):
    def test_manifest_declares_advisory_tools_and_secret(self):
        text = (ROOT / "plugin.yaml").read_text()
        for tool in ("jev_route_profile", "jev_suggest_skills", "jev_router_status"):
            self.assertIn(tool, text)
        self.assertIn("OPENROUTER_API_KEY", text)
        self.assertIn("secret: true", text)

    def test_no_execution_or_enablement_handlers(self):
        text = (ROOT / "tools.py").read_text()
        self.assertNotIn("delegate_task", text)
        self.assertNotIn("plugins enable", text)

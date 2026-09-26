"""Hermes tool schemas and advisory handlers."""
from __future__ import annotations

import json
from pathlib import Path

try:  # Hermes package import
    from .catalog import profile_catalog, skill_catalog
    from .routing import configured_transport, recommend
except ImportError:  # direct local execution
    from catalog import profile_catalog, skill_catalog
    from routing import configured_transport, recommend

ROUTE_PROFILE = {"name": "jev_route_profile", "description": "Advisory Jev recommendation of an eligible Hermes profile. Does not delegate or execute work.", "parameters": {"type": "object", "properties": {"request": {"type": "string"}}, "required": ["request"]}}
SUGGEST_SKILLS = {"name": "jev_suggest_skills", "description": "Advisory Jev recommendation of one relevant skill in a selected Hermes profile. Does not load a skill.", "parameters": {"type": "object", "properties": {"request": {"type": "string"}, "profile": {"type": "string"}}, "required": ["request", "profile"]}}
ROUTER_STATUS = {"name": "jev_router_status", "description": "Report local router catalog availability without making a network request.", "parameters": {"type": "object", "properties": {}}}


class Handlers:
    def __init__(self, ctx): self.ctx = ctx
    def _settings(self): return getattr(self.ctx, "config", {}).get("plugins", {}).get("entries", {}).get("jev-capability-router", {}).get("settings", {})
    def _home(self): return Path(getattr(self.ctx, "hermes_home", "~/.hermes")).expanduser()
    def route_profile(self, params, **_kwargs):
        settings, transport = self._settings(), configured_transport(self._settings())
        if not transport: return json.dumps({"selected": None, "reason": "OPENROUTER_API_KEY not configured"})
        return recommend(transport, params["request"], profile_catalog(self._home(), int(settings.get("profile_excerpt_chars", 1200))), model=settings.get("model", "typesafe/jev-1.13"), threshold=float(settings.get("profile_confidence", .7)), kind="Hermes profile").json()
    def suggest_skills(self, params, **_kwargs):
        settings, transport = self._settings(), configured_transport(self._settings())
        if not transport: return json.dumps({"selected": None, "reason": "OPENROUTER_API_KEY not configured"})
        return recommend(transport, params["request"], skill_catalog(self._home()/"profiles"/params["profile"], request=params["request"], limit=int(settings.get("skill_candidate_limit", 40))), model=settings.get("model", "typesafe/jev-1.13"), threshold=float(settings.get("skill_confidence", .55)), kind="Hermes skill").json()
    def status(self, _params, **_kwargs): return json.dumps({"profiles": len(profile_catalog(self._home())), "advisory_only": True, "transport_configured": configured_transport(self._settings()) is not None})

def make_handlers(ctx): return Handlers(ctx)

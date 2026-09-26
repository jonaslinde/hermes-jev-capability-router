"""Hermes entry point for the advisory Jev capability router."""
from __future__ import annotations

from .tools import ROUTE_PROFILE, ROUTER_STATUS, SUGGEST_SKILLS, make_handlers


def register(ctx):
    handlers = make_handlers(ctx)
    for schema, handler in ((ROUTE_PROFILE, handlers.route_profile), (SUGGEST_SKILLS, handlers.suggest_skills), (ROUTER_STATUS, handlers.status)):
        ctx.register_tool(name=schema["name"], toolset="jev_capability_router", schema=schema, handler=handler)

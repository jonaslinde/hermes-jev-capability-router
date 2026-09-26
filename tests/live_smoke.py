"""Opt-in live Jev smoke test. Never run this in CI."""
import os
import sys

from catalog import Candidate
from routing import configured_transport, recommend

if not os.getenv("OPENROUTER_API_KEY"):
    print("OPENROUTER_API_KEY is required; no request made.")
    raise SystemExit(2)

transport = configured_transport({})
result = recommend(transport, "Find primary-source background research", [Candidate("researcher", "Research primary sources and cite evidence.", "profile"), Candidate("maintainer", "Maintain Hermes installation.", "profile")], model="typesafe/jev-1.13", threshold=.0, kind="profile")
print(result.json())
raise SystemExit(0 if result.selected == "researcher" else 1)

# Hermes Jev Capability Router

An advisory-only [Hermes Agent](https://github.com/NousResearch/hermes-agent) plugin that uses TypeSafe Jev through OpenRouter's Decisions API to recommend:

- a Hermes profile for a request;
- relevant skills within that profile; and
- the smallest useful set of already available capabilities.

It never delegates work, changes the session model, enables a plugin, invokes an MCP server, or performs an external action. The host agent and Hermes policy remain responsible for those actions.

## Status

`0.1.1` is a tested routing foundation. It supports a live, file-derived profile/skill catalog and a pluggable Jev transport. Skill routing recursively discovers active (non-archived) skills, then sends Jev only the 40 lexically most relevant candidates to control token cost. Runtime tool, MCP and plugin discovery is deliberately exposed as an advisory extension point; automatic tool-schema pruning is not enabled in this release.

## Install

Install the verified release with Hermes. In a multiplexed gateway, native
plugins are profile-local: repeat these commands for every profile that should
be able to make Jev recommendations (the default profile is not shared with
named profiles).

```sh
hermes -p <profile> plugins install jonaslinde/hermes-jev-capability-router \
  --ref <full-40-character-commit-sha> --no-enable
hermes -p <profile> plugins enable jev-capability-router
hermes -p <profile> tools enable jev_capability_router --platform telegram
```

Use a full commit SHA for a reproducible rollout. A newer release can later be
adopted deliberately by updating the plugin and re-validating it.

Set `OPENROUTER_API_KEY` in the target profile's secret environment. The plugin uses the same OpenRouter Decisions endpoint and `typesafe/jev-1.13` model as the local pilot. In a multiplexed gateway the key is resolved at tool-call time from that profile's secret scope, not from the process environment. It sends only the request plus the eligible catalog entries needed for the decision; it never reads or transmits `.env` files.

## Validation

```sh
python3 -m unittest discover -s tests -v
hermes plugins validate .
hermes plugins compat .
```

The unit suite uses a fake transport and makes no network calls. `tests/live_smoke.py` is opt-in and requires `OPENROUTER_API_KEY`.

## Safety and privacy

- Results are recommendations, with `no_match` and `human_review` valid outcomes.
- A failed or malformed Jev response is fail-open: no recommendation is returned.
- Secrets and profile `.env` files are excluded from catalog discovery.
- Keep e-mail routing disabled until an explicit redaction policy is added.

See [SECURITY.md](SECURITY.md) and [baseline/README.md](baseline/README.md).

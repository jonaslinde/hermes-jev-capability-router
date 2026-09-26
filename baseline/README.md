# Fresh-session prompt baseline — 2026-09-26

Measured offline with `hermes --profile <name> prompt-size --json` on Hermes Agent `v0.21.5`.

| Metric across 12 profiles | Value |
| --- | ---: |
| Mean fixed system prompt | 33.0 KB |
| Mean tool-schema JSON | 53.9 KB |
| Mean registered tools | 32.9 |
| Approximate fixed prompt floor | 86.9 KB / ~22k rough tokens |
| Lowest fixed prompt floor | technical-operations-manager: 62.2 KB |
| Highest fixed prompt floor | recruiter: 101.3 KB |

This is a byte-based local estimate, not billable provider usage. It excludes conversation history and dynamically loaded skill bodies. The release evaluation must rerun this command before/after any schema-pruning middleware and add the Jev request tokens, latency, and provider-reported usage.

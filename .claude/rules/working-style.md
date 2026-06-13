# Working style — activist-os specifics

Universal agent autonomy/scope rules now live in the playbook:
`~/.claude/rules/playbook/agent-autonomy.md` (loaded automatically in every
repo). This file holds ONLY what's specific to activist-os.

## Product voice (for external-channel posts)

Serious, evidence-forward, constructive. No corporate-speak, no emoji excess.
The product's voice is the same in chat and on Discord.

## Keep the pre-kickoff checklist current

`web/checklist.html` is the living status board. After any meaningful unit of
work — a contract added, a stub agent written, the API booting, a smoke test
green — update the corresponding task's `class` (`done`, `partial`, or remove
`blocked`) and its `task-note` if stale. Not for cosmetic/doc-only changes.
Lives at `http://localhost:8080/checklist.html` (static server from `web/`).

## Test interpreter

`cd api && .venv/bin/python -m pytest tests/ -q` is the canonical test command —
the project venv, never a bare `python3`.

"""Band agent-credential config loader.

Reads ``agent_config.yaml`` (name → {agent_id, api_key}). Uses PyYAML when it's
available, otherwise a small fallback parser for the flat 2-level shape — so the
offline contract tests need no YAML dependency. Credentials live ONLY in this
file on disk (pointed at by ``AGENT_CONFIG_PATH``); never in the repo.
"""
from __future__ import annotations

from pathlib import Path


class BandConfigError(RuntimeError):
    """The Band agent config is missing or malformed."""


def _fallback_parse(text: str) -> dict[str, dict[str, str]]:
    config: dict[str, dict[str, str]] = {}
    current: str | None = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if not raw[0].isspace():
            current = raw.split(":", 1)[0].strip()
            config[current] = {}
        elif current is not None and ":" in raw:
            key, _, value = raw.strip().partition(":")
            config[current][key.strip()] = value.strip().strip('"').strip("'")
    return config


def load_agent_config(path: str | Path) -> dict[str, dict[str, str]]:
    path = Path(path)
    if not path.is_file():
        raise BandConfigError(f"agent config not found: {path}")

    text = path.read_text()
    try:
        import yaml

        raw = yaml.safe_load(text) or {}
    except ImportError:
        raw = _fallback_parse(text)

    agents: dict[str, dict[str, str]] = {}
    for name, creds in raw.items():
        if not isinstance(creds, dict) or "agent_id" not in creds or "api_key" not in creds:
            raise BandConfigError(
                f"agent '{name}' is missing agent_id/api_key in {path}"
            )
        agents[name] = {"agent_id": str(creds["agent_id"]), "api_key": str(creds["api_key"])}
    if not agents:
        raise BandConfigError(f"no agents defined in {path}")
    return agents

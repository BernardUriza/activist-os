"""Band agent-credential config loader.

Reads ``agent_config.yaml`` (name → {agent_id, api_key}). Uses PyYAML when it's
available, otherwise a small fallback parser for the flat 2-level shape — so the
offline contract tests need no YAML dependency. Credentials live ONLY in this
file on disk (pointed at by ``AGENT_CONFIG_PATH``); never in the repo.
"""
from __future__ import annotations

import base64
import binascii
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


def _load_yaml(text: str) -> dict:
    try:
        import yaml

        return yaml.safe_load(text) or {}
    except ImportError:
        return _fallback_parse(text)


def _parse_agents(raw: dict, source: str) -> dict[str, dict[str, str]]:
    agents: dict[str, dict[str, str]] = {}
    for name, creds in raw.items():
        if not isinstance(creds, dict) or "agent_id" not in creds or "api_key" not in creds:
            raise BandConfigError(f"agent '{name}' is missing agent_id/api_key in {source}")
        agents[name] = {"agent_id": str(creds["agent_id"]), "api_key": str(creds["api_key"])}
    if not agents:
        raise BandConfigError(f"no agents defined in {source}")
    return agents


def load_agent_config(path: str | Path) -> dict[str, dict[str, str]]:
    path = Path(path)
    if not path.is_file():
        raise BandConfigError(f"agent config not found: {path}")
    return _parse_agents(_load_yaml(path.read_text()), str(path))


def load_agent_config_from_b64(b64: str) -> dict[str, dict[str, str]]:
    try:
        text = base64.b64decode(b64, validate=True).decode("utf-8")
    except (binascii.Error, ValueError, UnicodeDecodeError) as exc:
        raise BandConfigError(f"AGENT_CONFIG_YAML_B64 is not valid base64 YAML: {exc}") from exc
    return _parse_agents(_load_yaml(text), "AGENT_CONFIG_YAML_B64")

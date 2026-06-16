"""Band agent config can be loaded from a file path OR an inline base64 env.

The deploy path (Azure Container Apps) cannot mount a secret file cheaply, so it
passes the YAML as AGENT_CONFIG_YAML_B64. BandTransport must resolve config from:
explicit config_path > AGENT_CONFIG_PATH > AGENT_CONFIG_YAML_B64.
"""
from __future__ import annotations

import base64

import pytest

from app.band_config import BandConfigError, load_agent_config_from_b64
from app.transports import BandTransport, BandTransportError

AGENT_NAMES = ["evidence", "campaign", "safety", "outreach", "coordinator", "reporter"]


def _yaml_text() -> str:
    return "".join(
        f'{name}:\n  agent_id: "id-{name}"\n  api_key: "key-{name}"\n' for name in AGENT_NAMES
    )


def _b64() -> str:
    return base64.b64encode(_yaml_text().encode("utf-8")).decode("ascii")


def test_load_agent_config_from_b64_parses_all_agents():
    configs = load_agent_config_from_b64(_b64())
    assert set(configs) == set(AGENT_NAMES)
    assert configs["safety"] == {"agent_id": "id-safety", "api_key": "key-safety"}


def test_load_agent_config_from_b64_rejects_garbage():
    with pytest.raises(BandConfigError):
        load_agent_config_from_b64("not-valid-base64!!!")


def test_band_transport_reads_b64_env_when_no_path(monkeypatch):
    monkeypatch.delenv("AGENT_CONFIG_PATH", raising=False)
    monkeypatch.setenv("AGENT_CONFIG_YAML_B64", _b64())
    transport = BandTransport(client_factory=lambda api_key: object())
    assert transport._configs["evidence"]["agent_id"] == "id-evidence"


def test_band_transport_path_takes_precedence_over_b64(monkeypatch, tmp_path):
    path = tmp_path / "agent_config.yaml"
    path.write_text(_yaml_text().replace("id-evidence", "from-file"))
    monkeypatch.setenv("AGENT_CONFIG_PATH", str(path))
    monkeypatch.setenv("AGENT_CONFIG_YAML_B64", _b64())
    transport = BandTransport(client_factory=lambda api_key: object())
    assert transport._configs["evidence"]["agent_id"] == "from-file"


def test_band_transport_no_config_anywhere_errors(monkeypatch):
    monkeypatch.delenv("AGENT_CONFIG_PATH", raising=False)
    monkeypatch.delenv("AGENT_CONFIG_YAML_B64", raising=False)
    with pytest.raises(BandTransportError):
        BandTransport(client_factory=lambda api_key: object())

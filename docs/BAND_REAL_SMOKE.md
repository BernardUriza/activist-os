# Real Band smoke — opt-in

The default test suite is **offline**: it exercises `BandTransport` against an
in-process fake client, so CI needs no network, no credentials, and no Band SDK.
The real Band path is **opt-in** and only runs when you enable it explicitly.

## What you need

| Variable | Meaning |
|---|---|
| `RUN_BAND_SMOKE=1` | Arms the opt-in smoke test (otherwise it skips). |
| `TRANSPORT=band` | Makes the API (`app.main`) use the real Band transport. |
| `BAND_REST_URL=https://app.band.ai` | Band REST endpoint (defaults to this if unset). |
| `AGENT_CONFIG_PATH=/abs/path/agent_config.yaml` | Local file with the agent credentials. |

You also need the Band SDK installed: `pip install band-sdk` (provides
`thenvoi_rest`). The offline path never imports it.

## `agent_config.yaml` shape

One entry per agent — `agent_id` + `api_key` from app.band.ai/agents. **This
file holds secrets: keep it OUTSIDE the repo** (e.g. `~/.secrets/`), never commit
it. Only `AGENT_CONFIG_PATH` points at it.

```yaml
evidence:
  agent_id: "ag_..."
  api_key: "sk_..."
campaign:
  agent_id: "ag_..."
  api_key: "sk_..."
safety:
  agent_id: "ag_..."
  api_key: "sk_..."
outreach:
  agent_id: "ag_..."
  api_key: "sk_..."
coordinator:
  agent_id: "ag_..."
  api_key: "sk_..."
reporter:
  agent_id: "ag_..."
  api_key: "sk_..."
```

`evidence` owns/initiates the room; `campaign, safety, outreach, coordinator` are
seated (owner + 4 = the 5-seat cap). `reporter` (and `system`) are virtual —
never seated; their legs ride as task events.

## Run it

```bash
cd api
RUN_BAND_SMOKE=1 \
TRANSPORT=band \
BAND_REST_URL=https://app.band.ai \
AGENT_CONFIG_PATH=/abs/path/agent_config.yaml \
pytest tests/contracts/test_real_band_smoke.py -q
```

The smoke asserts the same canonical contract as the offline tests: the 8-step
order, `veto_index=2` / `approved_index=4`, a real `band_room_id` on every
handoff, `band_message_id` on the non-virtual legs, `virtual=true` (and no
message id) on the reporter/system legs, and that `/history` + `/events` still
hold.

If it fails, classify before patching: missing credential · auth failure · room
creation · participant cap · message send · virtual event · contract mismatch.

## Default offline run (no Band)

```bash
cd api
pytest tests/contracts -q
pytest -q
ruff check app tests --isolated
```

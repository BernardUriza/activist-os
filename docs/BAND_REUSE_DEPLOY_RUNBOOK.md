# Band reuse_single deploy runbook (8B)

Copy/paste runbook to activate the `reuse_single` Band room strategy on the live
Azure Container App, with verification and rollback. **This document mutates
nothing.** Every Azure command below is for **Bernard** to run by hand — the
relay does not cross the firewall (no `az`, no deploy, no public smoke, no room
creation, no secrets).

> Prepared by the exchange-coagent relay (8B-prep). Validation was local only.

## 0. Prerequisite that the room strategy alone does NOT cover

`BAND_ROOM_STRATEGY=reuse_single` only changes room behaviour **when the API is
already running the real Band transport**. The current live deploy runs
`TRANSPORT=local` (see `docs/BAND_REAL_SMOKE.md`). Setting the strategy on a
`local` deploy is a no-op.

For a real Band smoke the Container App must have ALL of:

| Env var | Value | Why |
|---|---|---|
| `TRANSPORT` | `band` | Makes `app.main` use `BandTransport` (otherwise local) |
| `AGENT_CONFIG_YAML_B64` | `secretref:agent-config-b64` | The 6 agent creds (set out-of-band as a secret) |
| `BAND_ROOM_STRATEGY` | `reuse_single` | Reuse one existing room instead of creating per run |
| `BAND_REUSE_ROOM_ID` | `<existing-room-uuid>` | The room to reuse — owner + 4 seats already created |

If `TRANSPORT` is not already `band` in the live deploy, flipping it is itself a
behaviour change Bernard must decide on — it is not part of "just reuse a room".

## 1. Current state

- API: `https://activist-os-api.greenbay-d46a7a63.eastus.azurecontainerapps.io`
- Web: `https://proud-stone-023fae70f.7.azurestaticapps.net/app`
- Code: `8b128f3 feat(api): support Band room reuse strategy (create_per_run|reuse_single)` (on `origin/main`)
- Container App name: `activist-os-api`
- Resource group: the value of the GitHub Actions var `AZURE_RESOURCE_GROUP`
  (the workflows reference `${{ vars.AZURE_RESOURCE_GROUP }}`, not a literal).

## 2. Variables Bernard fills in

```bash
export AOS_RESOURCE_GROUP="<resource-group>"           # same as the AZURE_RESOURCE_GROUP repo var
export AOS_CONTAINER_APP="activist-os-api"
export BAND_REUSE_ROOM_ID="<existing-band-room-uuid>"  # an existing room with participants already seated
export AOS_API_KEY="<APP_API_KEY value the deploy uses>" # needed for the smoke (endpoint is auth-gated)
```

`BAND_REUSE_ROOM_ID` must be an existing room with its participants already
created (owner + 4 seats). The reuse path deliberately does NOT create
participants — that is the whole point.

## 3. Azure command — Bernard runs this, NOT the relay

```bash
az containerapp update \
  --resource-group "$AOS_RESOURCE_GROUP" \
  --name "$AOS_CONTAINER_APP" \
  --set-env-vars \
    TRANSPORT=band \
    BAND_ROOM_STRATEGY=reuse_single \
    BAND_REUSE_ROOM_ID="$BAND_REUSE_ROOM_ID"
```

`AGENT_CONFIG_YAML_B64` is assumed already wired as a secret
(`az containerapp secret set --name activist-os-api --secrets "agent-config-b64=<value>"`
then `--set-env-vars AGENT_CONFIG_YAML_B64=secretref:agent-config-b64`). If it is
not, set it BEFORE the command above or the Band transport boots without creds.

## 4. Single public smoke

The endpoint is auth-gated (`X-API-Key`), so the header is mandatory — a curl
without it returns `401`:

```bash
curl -s -X POST \
  "https://activist-os-api.greenbay-d46a7a63.eastus.azurecontainerapps.io/workflow/start" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $AOS_API_KEY" \
  -d '{"concern":"Restaurant compostable claim lacks local disposal evidence"}'
```

The body accepts `concern` (aliases `text`/`message`), optional `location`,
`category`. A `202` with `{"run_id": "...", "status": "..."}` means accepted.

Then:
- open `/app`
- confirm MODE LIVE
- confirm TRANSPORT BAND
- confirm the provenance chip shows the SAME reused room id
- confirm 6 messages · 2 virtual events

## 5. Critical log verification

Logs MUST show:

- NO `POST /agent/chats` (no new room created)
- NO participant creation
- YES 6 messages
- YES 2 virtual events (reporter/system legs ride as task events)
- the SAME reused room id as `BAND_REUSE_ROOM_ID`

If logs show a new room id or `POST /agent/chats`, the reuse path did not engage
— roll back and investigate before retrying.

## 6. Rollback

```bash
az containerapp update \
  --resource-group "$AOS_RESOURCE_GROUP" \
  --name "$AOS_CONTAINER_APP" \
  --set-env-vars BAND_ROOM_STRATEGY=create_per_run
```

Leaving `BAND_REUSE_ROOM_ID` set is harmless when `strategy=create_per_run`. To
return fully to the prior demo posture, also set `TRANSPORT=local`.

## What the relay did NOT do

- No `az containerapp update` / deploy
- No public smoke
- No room creation
- No secret touched
- No code change
- No commit (this file is left untracked for Bernard)

## Local validation performed (relay, offline)

```bash
cd api
pytest tests/contracts/test_band_room_reuse.py -q
ruff check --isolated app
python -m compileall app
```

Results are reported in the relay status, not asserted here.

# AOS deploy preflight — environment & domain manifest

Status: **LIVE (Jun 12)** — including the custom domain.
The deploy topology mirrors insult-ai (see `.claude/rules/cicd.md`).

## Live URLs

| Surface | URL |
|---|---|
| **Demo (official)** | **https://aos.bernarduriza.com** |
| Web (SWA) | https://proud-stone-023fae70f.7.azurestaticapps.net |
| API (Container Apps) | https://activist-os-api.greenbay-d46a7a63.eastus.azurecontainerapps.io |
| Resource group | `activist-os-rg` (eastus) · env `activist-os-env` |

DNS: `CNAME aos → proud-stone-023fae70f.7.azurestaticapps.net.` at Namecheap,
hostname bound on the SWA (`status: Ready`), TLS auto-issued. End-to-end smoke
from the domain: full Band workflow, STREAMING → LIVE API, 8 handoffs.

## Frontend (web)

| Item | Value |
|---|---|
| Intended domain | **aos.bernarduriza.com** (same apex as insult-ai's `iai.`, own subdomain) |
| Hosting | Azure Static Web Apps |
| Source repo | `free-intelligence` (monorepo) |
| App path | `apps/activist-os/web` |
| Build | `pnpm install && pnpm --filter activist-os-web build` → static export in `out/` |

Required env at build time:

```
NEXT_PUBLIC_ACTIVIST_API_URL=https://<AOS_API_URL>
```

`aos.bernarduriza.com` points at the **web app only** — the API gets its own
Container Apps URL, injected via the env var above. Never hardcode it.

The SWA build workflow belongs in `free-intelligence` (the repo that owns the
app path), not in activist-os.

## API

| Item | Value |
|---|---|
| Hosting | Azure Container Apps (fi-runner spawns subprocesses — FaaS cannot host this) |
| Source repo | `activist-os` |
| App path | `api/` |
| Image | `ghcr.io/bernarduriza/activist-os/api` (lowercase — GHCR rejects uppercase) |
| Liveness | `GET /health` — keyless, never gate it behind an API key |

Required env at runtime:

```
TRANSPORT=band
BAND_REST_URL=https://app.band.ai
BAND_VIRTUAL_AGENTS=reporter
AGENT_CONFIG_PATH=<container path to agent_config.yaml, mounted or materialized>
ACTIVIST_OS_ENV_FILE=<optional explicit env file path>
ANTHROPIC_AUTH_TOKEN=<secretref — az containerapp secret set>
```

Band agent credentials (`agent_config.yaml`) are **never** baked into the
image: materialize at runtime from a Container Apps secret, same pattern as
insult-ai's Claude OAuth token.

## Deploy blockers — status

| Blocker | Status |
|---|---|
| `band_agents/*.py` absolute Mac dotenv paths | **FIXED** — `band_agents/env.py` `load_local_env()`: `ACTIVIST_OS_ENV_FILE` > module-relative `api/.env` > `find_dotenv` |
| Regression guard | `api/tests/test_no_absolute_local_paths.py` scans `app/` + `band_agents/` and fails on any local path |

## Order of operations (when Bernard says "deploy now")

1. API: build image, create Container App manually (one `az` command), smoke `/health`.
2. Web: SWA from free-intelligence, point `NEXT_PUBLIC_ACTIVIST_API_URL` at the Container App URL.
3. DNS: CNAME `aos.bernarduriza.com` → SWA. Last step, never first.

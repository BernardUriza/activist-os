# Activist OS

**Safe, evidence-backed civic advocacy workflows.** Six specialized agents turn a
community concern into a verified campaign packet — with provenance, safety
review, and human-action tasks **before anything goes public**.

> Band coordinates the agents. FI preserves memory and provenance. Safety gates
> every public action.

Built for the **Band of Agents Hackathon** (lablab.ai) — Regulated &
High-Stakes Workflows.

## Live demo

| Surface | URL |
|---|---|
| Web (fi-glass chat + artifacts rail) | https://proud-stone-023fae70f.7.azurestaticapps.net/app |
| API | https://activist-os-api.greenbay-d46a7a63.eastus.azurecontainerapps.io |

Both halves auto-deploy on every push to `main` (path-scoped GitHub Actions).

## The problem

Advocacy is easy to start and easy to get wrong. Grassroots groups carry real
legal and safety exposure with no ops layer to catch it: an unsupported claim is
a defamation risk, a public campaign can accidentally escalate into harassment,
and volunteer teams burn out on coordination.

## How it works — six agents, one governed handoff chain

Each agent owns one role and exchanges structured context through Band. The
coordination is **visible, not narrated** — every handoff is rendered from the
real transport.

```
Evidence → Campaign → ⟳ Safety veto loop ⟲ → Outreach → Coordinator → Reporter → packet
                        (Campaign ⇄ Safety)
```

| Agent | Role |
|---|---|
| **Evidence** | Finds and verifies claims, attaching a provenance tier to every source. |
| **Campaign** | Turns verified evidence into a narrative — never beyond what the evidence supports. |
| **Safety** | **Veto power.** Blocks doxxing, harassment, unsupported accusations, and unsafe escalation before anything ships. |
| **Outreach** | Drafts posts, emails, flyers, public copy — in the community's language. |
| **Coordinator** | Converts the approved strategy into a concrete volunteer task board. |
| **Reporter** | Assembles the final provenance and audit packet, including every safety verdict. |

### The money shot — the safety veto loop

Safety can **veto the campaign before public release**, and the rejection is on
the record:

```
CAMPAIGN DRAFT  "Restaurant X is lying to its customers."
      ↓
VETO  defamation: unsupported accusation against a named target — blocked.
      ↓  revision → re-review
APPROVED  "Available evidence does not support the restaurant's 'compostable'
           claim under local disposal conditions."
```

The rejected revision ships **inside the packet** — governance that only shows
its approvals is marketing.

## What's in the repo

- **`api/`** — the coordination core. FastAPI on `app.main:app`, `TRANSPORT=local`
  (deterministic mock) or `TRANSPORT=band` (real Band agents — see
  [docs/BAND_REAL_SMOKE.md](docs/BAND_REAL_SMOKE.md)). SSE workflow stream. Exact
  behavioral contract in [docs/CANONICAL_CONTRACT.md](docs/CANONICAL_CONTRACT.md).
- **`web/`** — Next.js 16 + fi-glass + Tailwind v4:
  - **`/`** — the product landing.
  - **`/app`** — the live coordination console: fi-glass `AgentConversationSurface`
    as the primary chat surface (1 concern → 8 agent handoffs, VETO/APPROVED
    severity per message), artifacts rail (Safety Gate / Evidence Brief / Campaign
    Packet). Legacy dashboard preserved at `/app?dashboard=1`.

## Run it locally

```bash
# API
cd api
mamba env create -f environment.yml && conda activate app
export CLAUDE_CODE_OAUTH_TOKEN="$(claude setup-token)"   # or set APP_BACKEND=codex
uvicorn app.main:app --reload --port 8080
curl localhost:8080/health        # → {"status":"ok"}

# Web — in another shell
cd web
npm install
NEXT_PUBLIC_API_URL=http://localhost:8080 npm run dev    # → http://localhost:3000
```

Open `http://localhost:3000/` (landing) and `http://localhost:3000/app` (console).
The console opens on a reproducible cold-open mock — type a concern and hit Enter
for a live coordination.

### API surface

| Route | Purpose |
|---|---|
| `GET /health` | liveness (keyless — no auth required) |
| `POST /workflow/start` | start a coordination run → `{ run_id }` |
| `GET /workflow/{run_id}/events` | SSE stream (`handoff_sent…` → `stream_end`) |
| `GET /workflow/{run_id}/history` | full coordination record + artifacts |

See [docs/CANONICAL_CONTRACT.md](docs/CANONICAL_CONTRACT.md) for the exact
behavioral invariants (8-step order, veto indices, SSE terminal semantics).

## Deploy (Azure)

Path-scoped workflows trigger on push to `main`:
- `api/**` → Container Apps (OIDC + GHCR, `app.main:app`, port 8080)
- `web/**` → Static Web Apps (`next build` → `output: export`)

Auth: OIDC federated credential, subject
`repo:<owner>/<repo>:ref:refs/heads/main`. Required repo vars/secrets:
`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`,
`AZURE_CONTAINER_APP_NAME`, `AZURE_RESOURCE_GROUP`,
`AZURE_STATIC_WEB_APPS_API_TOKEN`, `NEXT_PUBLIC_API_URL`.

See `.github/workflows/` for the full CI spec.

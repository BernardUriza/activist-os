# CI/CD — Azure deployment (mirrors insult-ai pattern)

Activist OS follows the same deploy topology as
[insult-ai](https://github.com/BernardUriza/insult-ai) — two Azure targets,
OIDC auth, GHCR images, path-scoped workflows. Copy its workflow files and
adapt names; don't reinvent.

## Targets

| Component | Azure target | Why |
|---|---|---|
| `api/` (fi-runner agents + Band transport) | **Azure Container Apps** | fi-runner spawns subprocesses (`claude`, MCP servers) — FaaS cannot do this |
| `web/` (demo UI, Next.js) | **Azure Static Web Apps** | static export, zero servers needed |

**NEVER use serverless (Functions/Vercel) for the API.** fi-runner spawns external
CLI processes and MCP subprocesses. Any FaaS kills them on cold start. Container
Apps is the minimum viable host.

## Auth model — OIDC, not long-lived secrets

Use federated identity credentials, not a service principal secret stored as a
GitHub secret. The insult-ai federated credential `insult-ai-master` trusts GitHub's
OIDC issuer only when `subject == repo:BernardUriza/insult-ai:ref:refs/heads/master`.

For Activist OS: create a federated credential on the AAD app that trusts
`repo:BernardUriza/activist-os:ref:refs/heads/main`. Branch protection IS the
auth perimeter — adding a new branch requires a new federated credential, not
broadening the existing one.

GitHub Actions step (same as insult-ai):
```yaml
- name: Azure login (OIDC)
  uses: azure/login@v2
  with:
    client-id: ${{ vars.AZURE_CLIENT_ID }}
    tenant-id: ${{ vars.AZURE_TENANT_ID }}
    subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
```

## Workflow conventions (copy from insult-ai)

- **Path-scoped triggers** — `api/` workflow only fires on `api/**` changes;
  `web/` workflow only fires on `web/**`. Never re-deploy both halves on a
  docs-only commit.
- **Concurrency groups** — `cancel-in-progress: true` on the same ref. Racing
  two Container App revisions risks a half-rolled deploy.
- **Smoke test** — after every Container App update, probe `/health` (ungated,
  no X-API-Key) with a 90s retry loop. Fail the workflow if it never returns 200.
  Do NOT gate `/health` behind the API key — Container Apps' liveness probe needs
  it keyless.
- **`workflow_dispatch`** — always add the manual escape hatch.

## Image conventions

- Base: `quay.io/condaforge/miniforge3` (same as insult-ai) — fi-runner needs
  conda for Python + npm CLI installs in one image.
- Install CLIs at build time: `claude`, and whatever Band SDK requires.
- **Non-root user required.** Claude Code refuses to run as root. The
  Dockerfile must `useradd` and `USER` before the entrypoint.
- `entrypoint.sh` materializes `CLAUDE_CODE_OAUTH_TOKEN` →
  `~/.claude/.credentials.json` at runtime (never baked into the image).

## Registry — GHCR

Use `ghcr.io/bernarduriza/activist-os/api` (lowercase — GHCR rejects uppercase).
After the first successful push the package lands as `private`; flip it to
`public` once or add a PAT-backed registry credential to the Container App.

Compute tag:
```bash
IMG_LOWER=$(echo "ghcr.io/${{ env.IMAGE_NAME }}" | tr '[:upper:]' '[:lower:]')
echo "image=${IMG_LOWER}:${{ github.sha }}" >> "$GITHUB_OUTPUT"
```

## Secrets management — az CLI (never in the image, never committed)

Set secrets out-of-band via `az containerapp secret set`, not via workflow
env vars or committed config. Example for the Band API key:

```bash
az containerapp secret set \
  --name activist-os-api \
  --resource-group activist-os-rg \
  --secrets "band-api-key=$BAND_API_KEY"

az containerapp update \
  --name activist-os-api \
  --resource-group activist-os-rg \
  --set-env-vars "BAND_API_KEY=secretref:band-api-key"
```

Claude Code OAuth token (same pattern as insult-ai):
```bash
az containerapp secret set \
  --name activist-os-api \
  --resource-group activist-os-rg \
  --secrets "claude-oauth=$CLAUDE_CODE_OAUTH_TOKEN"
```

## Resource naming (to decide at kickoff)

| Resource | Suggested name |
|---|---|
| Resource group | `activist-os-rg` |
| Container App (API) | `activist-os-api` |
| Static Web App | `activist-os-web` |
| AAD app (CI identity) | `activist-os-ci` |
| Federated credential | `activist-os-main` |

## When to set this up

CI/CD is **not kickoff-week work**. Priority order (from `hackathon.md`):

1. Veto loop working (the differentiator)
2. One polished end-to-end case
3. **Demo URL the judges can touch** ← this is where CI/CD matters
4. Video + README + submission assets (Jun 18)

Stand up the Container App and Static Web App manually first (one `az` command
each). Wire the GitHub Actions workflows on Jun 17–18 once the core demo is
stable. Don't burn build days on infra automation before the product exists.

#!/bin/bash
# Activist OS API entrypoint. Materializes agent_config.yaml from the
# AGENT_CONFIG_YAML_B64 secret at runtime (never baked into the image),
# then serves FastAPI.
set -euo pipefail

echo "[entrypoint] activist-os api booting — python $(python -V 2>&1) | TRANSPORT=${TRANSPORT:-local}"

if [[ -n "${AGENT_CONFIG_YAML_B64:-}" ]]; then
  echo "$AGENT_CONFIG_YAML_B64" | base64 -d > /app/agent_config.yaml
  chmod 600 /app/agent_config.yaml
  echo "[entrypoint] agent_config.yaml materialized ($(grep -c agent_id /app/agent_config.yaml) agents)"
else
  echo "[entrypoint] WARN: AGENT_CONFIG_YAML_B64 unset — TRANSPORT=band will fail (local still works)"
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000

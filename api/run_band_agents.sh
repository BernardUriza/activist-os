#!/bin/bash
# Start all 6 Band agents as background processes.
# Prerequisites:
#   1. cp agent_config.yaml.template agent_config.yaml — fill in agent_id + api_key for each
#   2. Register all 6 agents at app.band.ai/agents (External Agent)
#   3. Redeem BANDHACK26 at band.ai for Band Pro access
#   4. ANTHROPIC_API_KEY in .env (or export it)

set -e

if [ ! -f agent_config.yaml ]; then
  echo "ERROR: agent_config.yaml not found."
  echo "Run: cp agent_config.yaml.template agent_config.yaml"
  echo "Then fill in the agent_id and api_key for each agent from app.band.ai/agents"
  exit 1
fi

VENV=".venv/bin/python"

echo "Starting 6 Band agents..."

$VENV band_agents/evidence_band_agent.py    &  PID_EVIDENCE=$!
$VENV band_agents/campaign_band_agent.py    &  PID_CAMPAIGN=$!
$VENV band_agents/safety_band_agent.py      &  PID_SAFETY=$!
$VENV band_agents/outreach_band_agent.py    &  PID_OUTREACH=$!
$VENV band_agents/coordinator_band_agent.py &  PID_COORDINATOR=$!
$VENV band_agents/reporter_band_agent.py    &  PID_REPORTER=$!

echo "All agents running:"
echo "  Evidence    PID=$PID_EVIDENCE"
echo "  Campaign    PID=$PID_CAMPAIGN"
echo "  Safety      PID=$PID_SAFETY"
echo "  Outreach    PID=$PID_OUTREACH"
echo "  Coordinator PID=$PID_COORDINATOR"
echo "  Reporter    PID=$PID_REPORTER"
echo ""
echo "Watch coordination at: https://app.band.ai"
echo ""
echo "To start a workflow:"
echo "  .venv/bin/python band_agents/orchestrator.py 'Your community concern here'"
echo ""
echo "Press Ctrl+C to stop all agents."

wait

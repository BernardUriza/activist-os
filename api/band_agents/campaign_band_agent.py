"""
Campaign Band Agent — turns EvidenceBrief into a campaign narrative.
Accepts Safety vetoes and rewrites. Sends CampaignPlan to @Safety.
Run as: python band_agents/campaign_band_agent.py
"""
import asyncio
import logging
from band import Agent
from oauth_adapter import make_adapter
from band.config import load_agent_config
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = """You are the Campaign Agent for Activist OS.

Your role: turn verified evidence into a campaign plan. Never go beyond what the evidence supports.

When you receive EVIDENCE_COMPLETE from @Evidence:
1. Build a campaign narrative using only claims with usable_in_campaign: true
2. Frame around the PATTERN (corporate practice), never the person
3. Language: factual, evidence-forward, constructive — never accusatory
4. Reply: "@Safety CAMPAIGN_DRAFT_READY\n<CampaignPlan JSON>"

When you receive NEEDS_REVISION from @Safety:
1. Read blocked_items carefully — each names exactly what to fix
2. Rewrite the flagged sections applying Safety's feedback
3. Increment the revision counter
4. Reply: "@Safety CAMPAIGN_REVISED\n<updated CampaignPlan JSON>"

CampaignPlan format:
{
  "run_id": "<uuid>",
  "narrative": "<evidence-backed campaign narrative>",
  "key_message": "<one sentence>",
  "actions": [
    {"id": "...", "description": "...", "channel": "flyer|social_media|email|...", "target_audience": "..."}
  ],
  "revision": 0
}

Forbidden phrases: "is lying", "is deceiving", "is a fraud", "is scamming" — use evidence-backed factual framing instead."""


async def main():
    load_dotenv('/Users/bernardurizaorozco/Documents/activist-os/api/.env')
    adapter = make_adapter(custom_section=SYSTEM_PROMPT)
    agent_id, api_key = load_agent_config("campaign")
    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
    logging.info("Campaign agent running...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())

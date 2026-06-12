"""
Evidence Band Agent — finds and verifies claims, sends EvidenceBrief to @Campaign.
Run as: python band_agents/evidence_band_agent.py
"""
import asyncio
import logging
from band import Agent
from oauth_adapter import make_adapter
from band.config import load_agent_config
from env import load_local_env

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = """You are the Evidence Agent for Activist OS — a multi-agent civic advocacy workflow.

Your role: receive a community concern and produce a verified EvidenceBrief with sourced claims.

When you receive a message with a community concern:
1. Analyze the concern and identify verifiable claims
2. For each claim, assess: supported / partial / unsupported
3. Assign a provenance tier: fetched_fulltext > news_search > company_source
4. Mark claims with usable_in_campaign: false if verdict is unsupported
5. Reply to @Campaign with the EvidenceBrief as JSON

EvidenceBrief format:
{
  "concern": "<original text>",
  "claims": [
    {
      "id": "<uuid>",
      "statement": "<factual claim>",
      "verdict": "supported|partial|unsupported",
      "confidence": 0.0-1.0,
      "usable_in_campaign": true|false,
      "sources": [
        {"url": "...", "title": "...", "provenance_tier": "fetched_fulltext|news_search|company_source", "quote": "..."}
      ]
    }
  ],
  "produced_at": "<ISO datetime>"
}

Reply format: "@Campaign EVIDENCE_COMPLETE\n<EvidenceBrief JSON>"

Be honest about what you can and cannot verify. Provenance integrity is non-negotiable."""


async def main():
    load_local_env()
    adapter = make_adapter(custom_section=SYSTEM_PROMPT)
    agent_id, api_key = load_agent_config("evidence")
    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
    logging.info("Evidence agent running...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())

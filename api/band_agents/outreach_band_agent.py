"""
Outreach Band Agent — drafts posts, emails, flyers. Only runs after Safety approves.
Output language mirrors the concern's language.
Run as: python band_agents/outreach_band_agent.py
"""
import asyncio
import logging
from band import Agent
from band.adapters.anthropic import AnthropicAdapter
from band.config import load_agent_config
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = """You are the Outreach Agent for Activist OS.

You only run after the Safety Agent has issued SAFETY_APPROVED. Never produce outreach for an unapproved plan.

When you receive SAFETY_APPROVED with a campaign plan:
1. Detect the language of the original community concern
2. Draft outreach copy IN THAT LANGUAGE (if concern is in Spanish, draft in Spanish)
3. Produce at minimum: one social post, one email template, one flyer text
4. Keep tone: factual, evidence-forward, constructive — no outrage theater
5. Reply: "@Coordinator OUTREACH_READY\n<OutreachPack JSON>"

OutreachPack format:
{
  "run_id": "...",
  "assets": [
    {"asset_type": "social_post", "channel": "instagram|twitter|facebook", "language": "en|es|...", "content": "..."},
    {"asset_type": "email", "channel": "direct", "language": "...", "content": "Subject: ...\n\n..."},
    {"asset_type": "flyer", "channel": "print", "language": "...", "content": "..."}
  ]
}

Forbidden: claims not in the approved campaign plan. Forbidden: personal names of private individuals."""


async def main():
    load_dotenv()
    adapter = AnthropicAdapter(
        model="claude-sonnet-4-6",
        custom_section=SYSTEM_PROMPT,
        enable_execution_reporting=True,
    )
    agent_id, api_key = load_agent_config("outreach")
    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
    logging.info("Outreach agent running...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())

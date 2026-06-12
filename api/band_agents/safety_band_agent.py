"""
Safety Band Agent — the veto gate. The money shot of the demo.
Runs 5 checks on every campaign draft. Only APPROVED unlocks Outreach.
Run as: python band_agents/safety_band_agent.py
"""
import asyncio
import logging
from band import Agent
from band.adapters.anthropic import AnthropicAdapter
from band.config import load_agent_config
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = """You are the Safety Agent for Activist OS. You hold veto power over every public action.

APPROVED is the ONLY status that unlocks Outreach. When in doubt, do not approve.
A false negative costs one revision cycle. A false positive could cost a lawsuit.

When @mentioned with a campaign plan, run ALL five checks:

1. DEFAMATION — does any public claim rest on partial/unsupported evidence, or overstate a supported one?
2. DOXXING — does any artifact contain personal data of a private individual?
3. HARASSMENT — does any action target a PERSON rather than a pattern or practice?
4. UNSUPPORTED_CLAIMS — does the narrative use any claim marked usable_in_campaign: false?
5. ESCALATION — does any action go beyond lawful, nonviolent organizing?

Response formats:

If ALL checks pass:
"@Campaign SAFETY_APPROVED\n{\"run_id\": \"...\", \"status\": \"approved\", \"blocked_items\": [], \"reviewer_notes\": \"All five checks passed.\"}"
Then also: "@Outreach SAFETY_APPROVED — proceed with campaign plan: <CampaignPlan JSON>"

If ANY check fails:
"@Campaign SAFETY_NEEDS_REVISION\n{\"run_id\": \"...\", \"status\": \"needs_revision\", \"blocked_items\": [{\"check\": \"defamation\", \"description\": \"...\", \"target\": \"...\"}], \"reviewer_notes\": \"...\"}"

If core claim is unsupported (no revision can fix):
"@Campaign SAFETY_BLOCKED\n{\"run_id\": \"...\", \"status\": \"blocked\", \"blocked_items\": [...], \"reviewer_notes\": \"Core claim unsupported — no revision can fix this.\"}"

Every verdict — including rejections — is visible in this room history. Governance that only shows approvals is marketing."""


async def main():
    load_dotenv()
    adapter = AnthropicAdapter(
        model="claude-sonnet-4-6",
        custom_section=SYSTEM_PROMPT,
        enable_execution_reporting=True,
    )
    agent_id, api_key = load_agent_config("safety")
    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
    logging.info("Safety agent running...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())

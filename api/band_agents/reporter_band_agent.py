"""
Reporter Band Agent — assembles the final CampaignPacket with full audit trail.
Governance that only shows approvals is marketing — the veto is in the packet.
Run as: python band_agents/reporter_band_agent.py
"""
import asyncio
import logging
from band import Agent
from oauth_adapter import make_adapter
from band.config import load_agent_config
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = """You are the Reporter Agent for Activist OS.

Your role: assemble the final CampaignPacket from all prior outputs and post it as the campaign's deliverable.

When you receive COORDINATOR_READY from @Coordinator:
1. Gather: EvidenceBrief + CampaignPlan + SafetyVerdict + OutreachPack + TaskBoard from the room history
2. Assemble the CampaignPacket — include the full audit trail, including any Safety vetoes
3. Post a summary message tagging all agents so humans can review
4. Use thenvoi_send_event to mark the workflow COMPLETED

Packet summary format to post:
"CAMPAIGN PACKET READY — run_id: <id>

Evidence: <N> claims verified
Campaign: revision <N>, approved by Safety
Outreach: <N> assets in <language>
Tasks: <N> volunteer tasks
Safety audit: <N> checks, <N> veto(s), final status: APPROVED

[HUMAN REVIEW REQUIRED before any public action]
Full packet: <CampaignPacket JSON>"

The full audit trail — including rejections — ships inside the packet.
Governance that only shows its approvals is marketing."""


async def main():
    load_dotenv('/Users/bernardurizaorozco/Documents/activist-os/api/.env')
    adapter = make_adapter(custom_section=SYSTEM_PROMPT)
    agent_id, api_key = load_agent_config("reporter")
    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
    logging.info("Reporter agent running...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())

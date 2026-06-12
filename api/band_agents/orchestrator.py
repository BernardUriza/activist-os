"""
Workflow orchestrator — creates a Band room, adds all 6 agents, and kicks off the workflow.
Run once per workflow: python band_agents/orchestrator.py "Your community concern here"

The agents then coordinate autonomously through Band. Watch the room in app.band.ai.
"""
import asyncio
import logging
import sys
from band import Agent
from oauth_adapter import make_adapter
from band.config import load_agent_config
from env import load_local_env

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = """You are the Orchestrator for Activist OS.

Your role: start the workflow by sending the community concern to @Evidence, then monitor progress.

When you receive a concern to process:
1. Call thenvoi_create_chatroom to create a new room named "Activist OS — <short concern description>"
2. Add all agents to the room: @Evidence @Campaign @Safety @Outreach @Coordinator @Reporter
3. Send the concern to @Evidence: "@Evidence WORKFLOW_START\n<concern text>"
4. Wait and monitor. The agents coordinate autonomously.

When @Reporter posts CAMPAIGN PACKET READY:
- The workflow is complete
- A human must review before any public action
- Post: "Workflow complete. Human review required before release."

You hold the send button. The system assembles; humans execute."""


async def main():
    load_local_env()

    concern = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else (
        "Restaurant X claims 100% compostable packaging, "
        "but local waste systems do not process it."
    )

    logging.info(f"Starting workflow for concern: {concern[:80]}...")

    adapter = make_adapter(custom_section=SYSTEM_PROMPT)

    agent_id, api_key = load_agent_config("evidence")  # uses Evidence creds to bootstrap
    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)

    # The orchestrator sends the initial message and the room takes over
    logging.info("Orchestrator ready. Sending concern to Evidence via Band room...")
    await agent.run()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py '<community concern>'")
        print("Default: using greenwashing demo case")
    asyncio.run(main())

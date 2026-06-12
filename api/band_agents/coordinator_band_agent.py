"""
Coordinator Band Agent — converts outreach into concrete volunteer tasks.
Run as: python band_agents/coordinator_band_agent.py
"""
import asyncio
import logging
from band import Agent
from oauth_adapter import make_adapter
from band.config import load_agent_config
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

SYSTEM_PROMPT = """You are the Coordinator Agent for Activist OS.

Your role: translate the approved outreach pack into a concrete volunteer task board.
Groups dissolve because coordinators burn out. You absorb the ops work.

When you receive OUTREACH_READY from @Outreach:
1. Break down each outreach asset into one or more actionable volunteer tasks
2. Include: title, description, channel, estimated_hours, materials_needed
3. Tasks should be completable by a volunteer with no specialist knowledge
4. Reply: "@Reporter COORDINATOR_READY\n<TaskBoard JSON>"

TaskBoard format:
{
  "run_id": "...",
  "tasks": [
    {
      "id": "...",
      "title": "...",
      "description": "Step-by-step instructions a volunteer can follow",
      "channel": "print|social_media|email|documentation",
      "estimated_hours": 0.5,
      "materials_needed": ["item1", "item2"]
    }
  ]
}

Be specific. "Distribute flyers" is not a task. "Print 100 copies of the attached flyer and hand them out near the main entrance on Saturday 10am-12pm" is a task."""


async def main():
    load_dotenv('/Users/bernardurizaorozco/Documents/activist-os/api/.env')
    adapter = make_adapter(custom_section=SYSTEM_PROMPT)
    agent_id, api_key = load_agent_config("coordinator")
    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
    logging.info("Coordinator agent running...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())

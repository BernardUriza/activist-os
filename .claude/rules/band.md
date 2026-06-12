# Band / Codeband — the hard requirement

Analog of insult-ai's `bright-data.md`: the sponsor tech is not decoration,
it is the graded surface.

## The requirement (verbatim from the event page)

> Build a multi-agent system where **at least 3 agents collaborate through
> Band** across planning, execution, review, decision-making, or task handoff.

Activist OS commits to 6 agents through Band. The minimum demonstrable bar
if everything burns: EVIDENCE → CAMPAIGN ⇄ SAFETY (3 agents, including a
review loop — the strongest possible "real coordination" proof).

## Integration doctrine

- **Our contracts ride inside Band messages.** Band owns transport,
  discovery and coordination; `contracts/*.schema.json` owns meaning.
  Validate payloads against the schema before sending and after receiving.
- **Prefer Band primitives over custom plumbing** (architecture rule #2).
  Anything Band does natively that we hand-roll is negative points twice.
- **Coordination must be visible.** The demo shows Band's message/handoff
  history, not a narrated claim that "agents talked".

## Confirmed at kickoff stream (Jun 12, 2026)

**Band is TWO different things** — confirmed from kickoff slide:

- **Band platform / API** — "A shared interaction layer for AI agents — communicate,
  exchange structured context, coordinate actions, and discover or recruit other agents
  across tools and frameworks." This is what Activist OS uses. **Core platform · required.**
- **Codeband** — "An open-source coding-agent orchestration project for collaborative
  implementation, planning, review, and coordination — a reference for multi-agent
  coding workflows." Open source. Track 2 reference. NOT our concern.

### Band Pro access — hackathon promo

**Code: `BANDHACK26`** — 1 month Band Pro free for hackathon participants.

Redeem at [band.ai](https://band.ai):
1. Sign up or log in
2. Manage Billing → Subscribe under Pro plan → Add promotion code
3. Enter `BANDHACK26` → add card info → Pro activated

**Do this before writing any BandTransport code.**

### Band Hacker Guide & confirmed URLs (scraped from lablab.ai event page, Jun 12)

| Resource | URL |
|---|---|
| Band website | https://www.band.ai/ |
| **Band Hacker Guide** | **https://www.band.ai/hacker-guide** |
| Band docs (root) | https://docs.band.ai/ |
| Band SDK Setup | https://docs.band.ai/integrations/sdks/tutorials/setup |
| Connect Remote Agent | https://docs.band.ai/getting-started/connect-remote-agent |
| Band Agent API | https://docs.band.ai/api/introduction |
| Band Discord | https://discord.com/invite/5YkNXmYfjk |

**Start here:** https://www.band.ai/hacker-guide → then SDK setup → then BandTransport.

## Primitive table — FILLED (from Band Hacker Guide, Jun 12 2026)

| Need | Band primitive | How |
|---|---|---|
| Agent identity / discovery | **Agent** — registered at app.band.ai/agents → External Agent. UUID + API key per agent | Register all 6 agents in the UI; store in `agent_config.yaml` |
| Typed message exchange | **Chat room** + **@mention** — only @mentioned agents see the message | `thenvoi_send_message` with `@{agent_name} {json_payload}` |
| Request/response (veto loop) | Chat room turn-taking via @mentions — Campaign `@Safety`, Safety replies `@Campaign` | The room IS the veto loop channel. Visible in Band history. |
| Long-running workflow state | Room-scoped context — `/context` endpoint rehydrates a restarting agent | One room per workflow run |
| Human-in-the-loop checkpoint | Human added as participant in the room — `thenvoi_add_participant` | Add Bernard before packet release |
| Coordination history / audit visibility | **Multi-agent observability** — every message, tool call, thought lands in a room-scoped replayable log | Built-in, zero extra code |
| SDK install + auth | `pip install "band-sdk[anthropic]"` → `AnthropicAdapter` + `agent_config.yaml` | See implementation section below |

## SDK — implementation facts (Jun 12 2026)

```bash
# Install
pip install "band-sdk[anthropic]"
# or for Claude Agent SDK
pip install "band-sdk[claude-sdk]"
```

```python
from thenvoi import Agent
from thenvoi.adapters import AnthropicAdapter
from thenvoi.config import load_agent_config

adapter = AnthropicAdapter(
    model="claude-sonnet-4-6",
    custom_section="<agent role prompt here>",
    enable_execution_reporting=True,
)
agent_id, api_key = load_agent_config("safety")   # reads agent_config.yaml
agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
await agent.run()   # persistent WebSocket, listens forever
```

`agent_config.yaml` (add to `.gitignore`):
```yaml
evidence:
  agent_id: "uuid-from-band-ui"
  api_key: "band-api-key"
campaign:
  agent_id: "..."
  api_key: "..."
safety:
  agent_id: "..."
  api_key: "..."
# ...outreach, coordinator, reporter
```

### Platform tools (auto-exposed to the LLM — no plumbing needed)

| Tool | What it does |
|---|---|
| `thenvoi_send_message` | Send a chat message with @mentions |
| `thenvoi_send_event` | Post a thought, error, or task progress event |
| `thenvoi_add_participant` | Add an agent or user to the room (HITL checkpoint) |
| `thenvoi_create_chatroom` | Spin up a new room |
| `thenvoi_lookup_peers` | Discover agents to recruit |

### Architecture implication for BandTransport

**This changes the agent model.** Each of our 6 agents must:
1. Be registered at app.band.ai/agents as an External Agent
2. Run as an independent process (`await agent.run()`)
3. Coordinate via @mentions in a shared room (one room per workflow run)

The veto loop over Band:
```
Campaign runs → sends "@Safety [CampaignPlan JSON]"
Safety receives → evaluates → sends "@Campaign VETO blocked_items=[...]"
Campaign receives veto → rewrites → sends "@Safety [revised CampaignPlan JSON]"
Safety approves → sends "@Coordinator [SafetyVerdict JSON]"
```

Everything is in the room history. Judges see the veto, the rewrite, the approval.

### WebSocket endpoint
```
wss://app.band.ai/api/v1/socket/websocket?api_key=<key>&vsn=2.0.0
```

## Operational facts — learned from the first real-Band smoke (Jun 12, 2026)

Distilled with the coagent after BandTransport went green against app.band.ai.

### Pin the Band REST base URL explicitly

Never rely on the `thenvoi_rest` default environment — it points at
`platform.dev.thenvoi.com`, a dev host that does not resolve and hangs
requests for the full 60s timeout with an empty error. Every REST client this
repo builds passes `base_url=https://app.band.ai` explicitly (override via
`BAND_REST_URL`). This is what the `band` SDK itself does internally.

### Respect the 5-participant room cap with virtual agents

Band rooms cap at **5 participants** on the current plan
(`403 limit_reached: max_chat_room_participants=5`). Assume the cap. Agents
beyond it — `reporter` by default — run as **virtual/backend agents** via
`BAND_VIRTUAL_AGENTS`: they are never added as room participants; their
handoffs ride as room task events emitted by the room owner. Semantic
identity stays `reporter` in the canonical history; only the operational
emitter changes. Virtualization is architecture, not weakness — say so in
the demo.

## Fallback posture

If a Band primitive is missing or broken mid-week, degrade gracefully:
keep the contract-validated handoff, implement the thinnest possible
custom bridge, and **document the gap honestly in the README** — judges
reward honest engineering over silent hacks.

"""
OAuthAnthropicAdapter — wraps AnthropicAdapter but uses the Claude Code
OAuth access token (sk-ant-oat01-*) via Bearer auth instead of an API key.

Usage:
    from oauth_adapter import make_adapter
    adapter = make_adapter(custom_section="Your system prompt here")
"""
import os
from anthropic import AsyncAnthropic
from band.adapters.anthropic import AnthropicAdapter


def make_adapter(custom_section: str, model: str = "claude-sonnet-4-6") -> AnthropicAdapter:
    token = os.environ.get("ANTHROPIC_AUTH_TOKEN")
    if not token:
        raise RuntimeError("ANTHROPIC_AUTH_TOKEN not set — run: security find-generic-password -s 'Claude Code-credentials' -w | python3 -c \"import sys,json; print(json.loads(sys.stdin.read())['claudeAiOauth']['accessToken'])\" >> api/.env")

    adapter = AnthropicAdapter(
        model=model,
        custom_section=custom_section,
        enable_execution_reporting=True,
    )
    # Replace the SDK client with one that uses Bearer auth (OAuth token)
    adapter.client = AsyncAnthropic(auth_token=token)
    return adapter

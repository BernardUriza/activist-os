"""
Environment loading for Band agents — no absolute local paths (cicd.md rule).

Resolution order:
1. ACTIVIST_OS_ENV_FILE — explicit override (container/CI sets this).
2. api/.env next to this package — the local-dev default, module-relative.
3. find_dotenv from the working directory — last-resort discovery.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv


def load_local_env(override: bool = False) -> None:
    env_file = os.getenv("ACTIVIST_OS_ENV_FILE")
    if env_file:
        load_dotenv(env_file, override=override)
        return

    module_local = Path(__file__).resolve().parent.parent / ".env"
    if module_local.exists():
        load_dotenv(module_local, override=override)
        return

    discovered = find_dotenv(usecwd=True)
    if discovered:
        load_dotenv(discovered, override=override)

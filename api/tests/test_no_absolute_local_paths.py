"""
Guardrail: runtime code must never hardcode absolute dev-machine paths
(cicd.md rule "No absolute local paths in runtime code"). The concrete
failure this prevents: band_agents/*.py shipped load_dotenv with a Mac
path that worked locally and died silently inside the Azure container.
"""
from pathlib import Path

API_ROOT = Path(__file__).resolve().parent.parent

SCANNED_DIRS = ["app", "band_agents"]

# Assembled at runtime so this test file never matches its own patterns.
FORBIDDEN = [
    "/" + "Users/",
    "bernard" + "urizaorozco",
    "Desktop" + "/",
    "Documents/" + "free-intelligence",
    "Documents/" + "activist-os",
]


def test_runtime_code_has_no_absolute_local_paths():
    offenders: list[str] = []
    for dirname in SCANNED_DIRS:
        for path in (API_ROOT / dirname).rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in FORBIDDEN:
                if pattern in text:
                    offenders.append(f"{path.relative_to(API_ROOT)}: contains '{pattern}'")
    assert not offenders, (
        "Absolute local paths found in runtime code (breaks Azure containers):\n"
        + "\n".join(offenders)
    )

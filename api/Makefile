.PHONY: dev smoke test

VENV_PYTHON := .venv/bin/python
VENV_UVICORN := .venv/bin/uvicorn

dev:
	$(VENV_UVICORN) app.main:app --reload --port 8000

smoke:
	@echo "Running smoke test — greenwashing case..."
	$(VENV_PYTHON) -m pytest tests/test_smoke.py -v

test:
	$(VENV_PYTHON) -m pytest tests/ -v

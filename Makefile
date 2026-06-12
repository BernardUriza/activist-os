FI_REPO     := $(shell cd .. && pwd)/free-intelligence
WEB_DIR     := $(FI_REPO)/apps/activist-os/web
API_DIR     := $(shell pwd)/api
VENV_PYTHON := $(API_DIR)/.venv/bin/python
VENV_UVICORN := $(API_DIR)/.venv/bin/uvicorn

.PHONY: dev dev-api dev-web install test smoke

dev: ## Start API (:8000) + web (:3001) concurrently
	@echo "Starting Activist OS dev stack..."
	@trap 'kill 0' INT; \
	  (cd $(API_DIR) && $(VENV_UVICORN) app.main:app --reload --port 8000) & \
	  (cd $(WEB_DIR) && pnpm dev) & \
	  wait

dev-api: ## Start only the FastAPI backend
	cd $(API_DIR) && $(VENV_UVICORN) app.main:app --reload --port 8000

dev-web: ## Start only the Next.js frontend
	cd $(WEB_DIR) && pnpm dev

install: ## Install JS deps for the React app
	cd $(WEB_DIR) && pnpm install

test:
	cd $(API_DIR) && $(VENV_PYTHON) -m pytest tests/ -v

smoke:
	cd $(API_DIR) && $(VENV_PYTHON) -m pytest tests/test_smoke.py -v

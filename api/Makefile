.PHONY: dev smoke test

dev:
	uvicorn app.main:app --reload --port 8000

smoke:
	@echo "Running smoke test — greenwashing case..."
	python -m pytest tests/test_smoke.py -v

test:
	python -m pytest tests/ -v

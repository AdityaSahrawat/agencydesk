.PHONY: dev migrate migration seed test stop

dev:
	uv run alembic upgrade head
	uv run python seed.py
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	uv run alembic upgrade head

migration:
	uv run alembic revision --autogenerate -m "$(m)"

seed:
	uv run python seed.py

test:
	uv run pytest

stop:
	lsof -ti:8000 | xargs kill -9 2>/dev/null || true

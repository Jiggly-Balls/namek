.PHONY: ruff check run

all: ruff

ruff:
	uv run --dev ruff format
	uv run --dev  ruff check --fix --unsafe-fixes

check:
	uv run --dev basedpyright .

dev:
	uv run python -m namek

docker:
	docker compose up -d --build
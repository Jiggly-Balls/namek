.PHONY: ruff check run

all: ruff

ruff:
	uv run --dev ruff format
	uv run --dev  ruff check --fix

check:
	uv run --dev basedpyright .

venv:
	py -m venv .venv

run:
	.venv\Scripts\Activate.ps1
	py -m namek
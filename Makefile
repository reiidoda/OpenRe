.PHONY: install lint test typecheck check run-example

install:
	python -m pip install -e .[dev]

lint:
	ruff check src tests examples scripts

test:
	pytest

typecheck:
	mypy src

check: lint test typecheck

run-example:
	python examples/run_single_agent.py

.PHONY: install lint test typecheck check precommit run-example

PYTHON ?= python3

install:
	$(PYTHON) -m pip install -e .[dev]

lint:
	ruff check src tests examples scripts

test:
	pytest

typecheck:
	mypy src

check: lint test typecheck

precommit:
	pre-commit run --all-files

run-example:
	$(PYTHON) examples/run_single_agent.py

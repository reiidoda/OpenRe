.PHONY: install lint test typecheck docs-check check precommit run-example

PYTHON ?= python3

install:
	$(PYTHON) -m pip install -e .[dev]

lint:
	ruff check src tests examples scripts

test:
	pytest

typecheck:
	mypy src

docs-check:
	$(PYTHON) scripts/check_markdown_links.py

check: lint test typecheck docs-check

precommit:
	pre-commit run --all-files

run-example:
	$(PYTHON) examples/run_single_agent.py

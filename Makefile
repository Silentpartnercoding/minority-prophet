PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
BOOTSTRAP_PYTHON ?= python3
BASE ?= $(shell git merge-base origin/main HEAD 2>/dev/null || git rev-parse HEAD^)
HEAD_REF ?= HEAD

.PHONY: help setup verify verify-python verify-integrity verify-site \
	check-public-boundary check-public-boundary-sweep check-withheld-leak check-registration-chain \
	check-research-integrity

help:
	@echo "make setup       Create local Python and Node development dependencies"
	@echo "make verify      Run every required local check"
	@echo "make verify-python"
	@echo "make verify-integrity BASE=origin/main HEAD_REF=HEAD"
	@echo "make verify-site"

setup:
	"$(BOOTSTRAP_PYTHON)" -m venv .venv
	.venv/bin/python -m pip install --upgrade pip pytest
	npm ci

verify: verify-python verify-integrity verify-site

verify-python:
	PYTHONPATH=. "$(PYTHON)" -m pytest -q

verify-integrity: check-public-boundary check-public-boundary-sweep check-withheld-leak check-registration-chain check-research-integrity

check-public-boundary:
	"$(PYTHON)" scripts/check_public_boundary.py --base "$(BASE)" --head "$(HEAD_REF)"

# The diff check inspects additions only, so a term added to the blocklist today
# is never applied to anything committed yesterday. This reconciles the whole
# published tree. Without this target, routing CI through make would have dropped
# the sweep silently.
check-public-boundary-sweep:
	"$(PYTHON)" scripts/check_public_boundary.py --sweep --head "$(HEAD_REF)"

check-withheld-leak:
	"$(PYTHON)" scripts/check_withheld_leak.py --base "$(BASE)" --head "$(HEAD_REF)"

check-registration-chain:
	"$(PYTHON)" scripts/check_registration_chain.py --ref "$(HEAD_REF)"

check-research-integrity:
	"$(PYTHON)" scripts/check_research_integrity.py --base "$(BASE)" --head "$(HEAD_REF)"

verify-site:
	npm run lint
	npm test

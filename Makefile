PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
BOOTSTRAP_PYTHON ?= python3
BASE ?= $(shell git merge-base origin/main HEAD 2>/dev/null || git rev-parse HEAD^)
HEAD_REF ?= HEAD

.PHONY: help setup paper-setup paper-pdf paper-check verify verify-python verify-integrity verify-site verify-evaluation \
	check-doc-navigation \
	check-public-boundary check-public-boundary-sweep check-withheld-leak check-registration-chain \
	check-research-integrity check-canonical-model

help:
	@echo "make setup       Create local Python and Node development dependencies"
	@echo "make paper-setup Install the pinned peer-review PDF dependency"
	@echo "make paper-pdf   Build the peer-review manuscript PDF"
	@echo "make paper-check Validate the peer-review source, metadata, citations, and PDF"
	@echo "make verify      Run every required local check"
	@echo "make verify-python"
	@echo "make verify-integrity BASE=origin/main HEAD_REF=HEAD"
	@echo "make verify-site"
	@echo "make verify-evaluation"
	@echo "make check-doc-navigation"
	@echo "make check-canonical-model"

setup:
	"$(BOOTSTRAP_PYTHON)" -m venv .venv
	.venv/bin/python -m pip install --upgrade pip pytest
	npm ci

paper-setup:
	"$(PYTHON)" -m pip install -r requirements-paper.txt

paper-pdf:
	"$(PYTHON)" scripts/build_peer_review_pdf.py

paper-check: paper-pdf
	"$(PYTHON)" scripts/check_peer_review_package.py
	pdfinfo output/pdf/minority-prophet-peer-review-v1.2.0.pdf | rg "^(Pages|Page size|PDF version):"

verify: verify-python verify-integrity verify-site verify-evaluation

verify-python:
	PYTHONPATH=. "$(PYTHON)" -m pytest -q

verify-integrity: check-canonical-model check-doc-navigation check-public-boundary check-public-boundary-sweep check-withheld-leak check-registration-chain check-research-integrity check-gate-coverage check-criterion-reachability

check-canonical-model:
	"$(PYTHON)" scripts/check_canonical_model.py

check-doc-navigation:
	"$(PYTHON)" scripts/check_documentation_navigation.py

# The only gate here that examines a CRITERION rather than an artifact. Every
# other check passed on HGD-1 while HGD-1g demanded a 5-point error reduction
# from a 4.349-point baseline -- unsatisfiable by any possible result, and
# invisible to a check that only ever looks at what was produced.
check-criterion-reachability:
	"$(PYTHON)" scripts/check_criterion_reachability.py

check-gate-coverage:
	"$(PYTHON)" scripts/check_gate_coverage.py

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

verify-evaluation:
	npm --prefix evaluations/multi-model-v1 test

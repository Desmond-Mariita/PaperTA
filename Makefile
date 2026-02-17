PHASE ?= 1
LOOP ?= design

.PHONY: gate-design gate-build verify-reviews verify-checklist verify-external run-external check-docstrings phase-report

gate-design:
	python3 scripts/phase_gate.py --phase $(PHASE) --loop design

gate-build:
	python3 scripts/phase_gate.py --phase $(PHASE) --loop build

verify-reviews:
	python3 scripts/verify_internal_reviews.py --phase $(PHASE) --loop $(LOOP)

verify-checklist:
	python3 scripts/verify_checklist.py --checklist docs/checklists/PHASE$(PHASE)_ACCEPTANCE_CHECKLIST.yaml --report-out reports/phase$(PHASE)/checklist_report.json

verify-external:
	python3 scripts/verify_external_reviews.py --phase $(PHASE) --loop $(LOOP)

run-external:
	python3 scripts/run_external_reviews.py --phase $(PHASE) --loop $(LOOP) --context-file docs/ROADMAP_SUMMARY.md

check-docstrings:
	python3 scripts/check_docstrings.py --paths src/paperta --output reports/phase$(PHASE)/guidelines_report.json

phase-report:
	python3 scripts/generate_phase_report.py --phase $(PHASE) --loop $(LOOP)

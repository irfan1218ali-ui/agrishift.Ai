.PHONY: help validate
help:
	@echo "Foundation repository; see README.md and docs/development/phases.md"
validate:
	python scripts/validation/validate_foundation.py
	python scripts/validation/validate_six_sources.py

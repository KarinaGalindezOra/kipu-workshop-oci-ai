.DEFAULT_GOAL := help

.PHONY: help setup test lint terraform-fmt terraform-validate

help:
	@echo "setup              Create the Python virtual environment and install Workshop 1 dependencies"
	@echo "test               Run Workshop 1 local unit tests"
	@echo "lint               Check the Streamlit UI"
	@echo "terraform-fmt      Format Workshop 1 Terraform files"
	@echo "terraform-validate Validate the selected Terraform environment after init"

setup:
	python -m venv .venv
	.\.venv\Scripts\python -m pip install --upgrade pip
	.\.venv\Scripts\python -m pip install -e ".[dev,lab01,ui]"

test:
	python -m pytest labs/lab01_agent_memory/tests -q

lint:
	python -m ruff check labs/lab01_agent_memory/ui/app.py

terraform-fmt:
	terraform fmt -recursive terraform

terraform-validate:
	terraform -chdir=terraform/environments/trial-team validate

.DEFAULT_GOAL := help

.PHONY: help setup test lint lab01-demo lab01-evidence lab02-demo lab02-evidence lab03-demo lab03-evidence terraform-fmt terraform-validate

help:
	@echo "setup              Create the Python virtual environment and install development dependencies"
	@echo "test               Run local unit tests"
	@echo "lint               Run Ruff"
	@echo "lab01-demo         Run the offline Lab 1 token comparison demo"
	@echo "lab01-evidence     Generate Lab 1 JSON, Markdown, and SVG evidence artifacts"
	@echo "lab02-demo         Run the offline Lab 2 contract retrieval demo"
	@echo "lab02-evidence     Generate Lab 2 grounded retrieval evidence"
	@echo "lab03-demo         Run the Lab 3 API-change analysis demo"
	@echo "lab03-evidence     Generate Lab 3 analysis and patch evidence"
	@echo "terraform-fmt      Format Terraform files"
	@echo "terraform-validate Validate the selected Terraform environment after init"

setup:
	python -m venv .venv
	.\.venv\Scripts\python -m pip install --upgrade pip
	.\.venv\Scripts\python -m pip install -e ".[dev,lab01,lab02,lab03,ui]"

test:
	python -m pytest

lint:
	python -m ruff check .

lab01-demo:
	python -m lab01_agent_memory.demo --team-id team-01

lab01-evidence:
	python -m lab01_agent_memory.demo --team-id team-01 --output-dir artifacts/lab01/team-01

lab02-demo:
	python -m lab02_contract_rag.demo

lab02-evidence:
	python -m lab02_contract_rag.demo --output-dir artifacts/lab02/team-01

lab03-demo:
	python -m lab03_api_change.demo

lab03-evidence:
	python -m lab03_api_change.demo --output-dir artifacts/lab03/team-01

terraform-fmt:
	terraform fmt -recursive terraform

terraform-validate:
	terraform -chdir=terraform/environments/trial-chicago validate

.PHONY: venv install clean bootstrap install-argocd run-all setup-oauth verify-images

PYTHON := python3
VENV_DIR := .venv
BIN := $(VENV_DIR)/bin

venv:
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)"

install: venv
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt
	@echo "Dependencies installed"

clean:
	rm -rf $(VENV_DIR)
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

bootstrap: install
	$(BIN)/python scripts/bootstrap.py

install-argocd: install
	$(BIN)/python scripts/install_argocd.py

run-all: install
	$(BIN)/python scripts/run_all.py

setup-oauth: install
	$(BIN)/python scripts/setup_oauth.py

verify-images: install
	$(BIN)/python scripts/verify_images.py $(ARGS)

help:
	@echo "Available targets:"
	@echo "  venv          - Create virtual environment"
	@echo "  install       - Install dependencies"
	@echo "  bootstrap     - Run K3s bootstrap script"
	@echo "  install-argocd - Install ArgoCD"
	@echo "  run-all       - Run full bootstrap process"
	@echo "  setup-oauth   - Setup OAuth with Keycloak"
	@echo "  verify-images - Verify container images (use ARGS for extra args)"
	@echo "  clean         - Remove virtual environment and cache files"

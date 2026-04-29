.PHONY: venv install clean bootstrap install-argocd services setup-oauth setup-routes post-install verify-images

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

services: install
	$(BIN)/python scripts/services.py

setup-oauth: install
	$(BIN)/python scripts/setup_oauth.py

setup-routes: install
	$(BIN)/python scripts/setup_routes.py $(ARGS)

post-install: install
	$(BIN)/python scripts/services.py
	$(BIN)/python scripts/setup_oauth.py
	$(BIN)/python scripts/setup_routes.py

verify-images: install
	$(BIN)/python scripts/verify_images.py $(ARGS)

help:
	@echo "Available targets:"
	@echo "  venv          - Create virtual environment"
	@echo "  install       - Install dependencies"
	@echo "  bootstrap     - Run K3s bootstrap script"
	@echo "  install-argocd - Install ArgoCD"
	@echo "  services      - Run full bootstrap process"
	@echo "  setup-oauth   - Setup OAuth with Keycloak"
	@echo "  setup-routes  - Patch Traefik IngressRoute hostnames from config.yaml"
	@echo "  post-install  - Run services + oauth + routes (full post-install sequence)"
	@echo "  verify-images - Verify container images (use ARGS for extra args)"
	@echo "  clean         - Remove virtual environment and cache files"

CURRENT_DIR := $(shell pwd)

VIRTUALENV_DIR = .env

help:
	@echo "Usage: $ make <target>"
	@echo " > env    : enable virtual env"
	@echo " > deps   : install dependencies"
	@echo " > tests  : run tests "

env:
	@echo "[RUN]: create/activate virtualenv"
	@virtualenv -p python3 $(VIRTUALENV_DIR) && \
	. $(VIRTUALENV_DIR)/bin/activate

deps: env
	@echo "[RUN]: install dependencies"
	$(VIRTUALENV_DIR)/bin/pip install -r $(CURRENT_DIR)/requirements.txt

tests: env
	@echo "[RUN]: tests"
	.env/bin/pytest tests

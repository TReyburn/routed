SHELL := /bin/bash

# If virtualenv exists, use it. If not, use PATH to find
SYSTEM_PYTHON  = $(shell which python3.10)
PYTHON         = $(or $(wildcard venv/bin/python), $(SYSTEM_PYTHON))


# primary targets
.PHONY: all
all: lint test

.PHONY: lint
lint: black isort mypy pylint

.PHONY: setup
setup: clean venv deps

.PHONY: setup-dev
setup-dev: clean create-venv deps-dev


# handling dependencies
.PHONY: deps
deps:
	$(PYTHON) -m pip install --upgrade pip -r requirements.txt

.PHONY: freeze
freeze:
	$(PYTHON) -m pip freeze > requirements.txt

.PHONY: deps-dev
deps-dev:
	$(PYTHON) -m pip install --upgrade pip -r requirements-dev.txt

.PHONY: freeze-dev
freeze-dev:
	$(PYTHON) -m pip freeze > requirements-dev.txt


# lint
.PHONY: black
black:
	$(PYTHON) -m black ./src

.PHONY: isort
isort:
	$(PYTHON) -m isort ./src

.PHONY: mypy
mypy:
	$(PYTHON) -m mypy ./src

.PHONY: pylint
pylint:
	$(PYTHON) -m pylint ./src


# test
.PHONY: test
test:
	echo "forgot to implement testing"


# handling environment
.PHONY: clean
clean:
	rm -rf ./venv
	rm -rf ./.mypy_cache

.PHONY: create-venv
create-venv:
	$(SYSTEM_PYTHON) -m venv ./venv


#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = dataset-template
PYTHON_VERSION = 3.10
PYTHON_INTERPRETER = python

#################################################################################
# COMMANDS                                                                      #
#################################################################################


## Install Python Dependencies
.PHONY: requirements
requirements:
	$(PYTHON_INTERPRETER) -m pip install -U pip
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8 and black (use `make format` to do formatting)
.PHONY: lint
lint:
	flake8 src
	isort --check --diff --profile black src
	black --check --config pyproject.toml src

## Format source code with black
.PHONY: format
format:
	black --config pyproject.toml src

## Set up python interpreter environment
.PHONY: create_environment
create_environment:
	pipenv --python $(PYTHON_VERSION)
	@echo ">>> New pipenv created. Activate with:\npipenv shell"


## Install this project for development
.PHONY: install
install:
	make requirements
	pre-commit install
	git lfs install
	dvc pull


#################################################################################
# PROJECT RULES                                                                 #
#################################################################################


# # Make Dataset
# .PHONY: data
# data: requirements
# 	$(PYTHON_INTERPRETER) src/dataset.py


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

# Print help message
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)

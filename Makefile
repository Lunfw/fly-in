PY	= python3
MAKEFLAGS	+= --no-print-directory
.DEFAULT_GOAL	:= help
VENV	= .venv
NORM	= $(VENV)/bin/flake8 && $(VENV)/bin/mypy .
RED	= \033[1;31m
GREEN	= \033[1;32m
CYAN	= \033[1;36m
RESET	= \033[0m

install:
	@if [ ! -d $(VENV) ]; then \
		$(PY) -m venv $(VENV); \
		$(VENV)/bin/pip install -r requirements.txt -q; \
	else \
		echo "#	$(RED)$(VENV) exists.$(RESET)"; \
		make help; \
	fi

help:
	@echo "\nUsage:"; \
	echo "$(CYAN)make install$(RESET)	-	installs .venv + requirements.txt"; \
	echo "$(CYAN)make run$(RESET)	-	runs the program"; \
	echo "$(CYAN)make debug$(RESET)	-	runs pdb on the command line"; \
	echo "$(CYAN)make clean$(RESET)	-	deletes cache, temp files, eventually the venv is there is one"; \
	echo "$(CYAN)make lint$(RESET)	-	runs flake8 & mypy"; \
	echo "$(CYAN)make lint-strict$(RESET)	- runs make lint, in strict mode"; \
	echo "$(CYAN)make help/make$(RESET)	-	this screen"

run:
	@if [ ! -d $(VENV) ]; then \
		make install; \
		fi
	@echo "\0"
	$(PY) -m src.main

lint:
	@if [ ! -d $(VENV) ]; then \
		make install; \
	$(NORM)

lint-strict:
	make lint --strict

clean:
	rm -rf $(VENV)
	rm -rf **/__pycache__
	rm -rf **/*.pyc
	rm -rf **/*.pyo

.PHONY: help run install clean lint lint-strict

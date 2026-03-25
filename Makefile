MAKEFLAGS	+= --no-print-directory
.DEFAULT_GOAL	:= help
VENV	= .venv
PY	= python3
RED	= \033[1;31m
BOLD	= \033[1m
GREEN	= \033[1;32m
CYAN	= \033[1;36m
GREY	= \033[1;90m
RESET	= \033[0m

install:
	@if [ ! -d $(VENV) ]; then \
		$(PY) -m venv $(VENV); \
		$(VENV)/bin/pip install -r requirements.txt -q; \
		chmod +x $(VENV)/bin/activate; \
	else \
		echo "#	$(RED)$(VENV) exists.$(RESET)"; \
		make help; \
	fi

help:
	@echo "\nUsage:"; \
	echo "$(CYAN)make install$(RESET)		-	installs .venv + requirements.txt"; \
	echo "$(CYAN)make run$(RESET)		-	runs the program"; \
	echo "$(CYAN)make debug$(RESET)		-	runs pdb on the command line"; \
	echo "$(CYAN)make clean$(RESET)		-	deletes cache, temp files, eventually the venv is there is one"; \
	echo "$(CYAN)make lint$(RESET)		-	runs flake8 & mypy"; \
	echo "$(CYAN)make lint-strict$(RESET)	-	runs make lint, in strict mode"; \
	echo "$(CYAN)make help/make$(RESET)		-	this screen"

run:
	@if [ ! -d $(VENV) ]; then \
		make install; \
		echo "$(BOLD)run $(VENV)/bin/activate first.$(RESET)"; \
		exit; \
	fi; \
	echo "$(BOLD)$(VENV)/bin/$(PY) -m src.main$(RESET)"; \
	sleep 0.5; \
	clear; \
	$(VENV)/bin/$(PY) -m src.main

debug:
	@if [ ! -d '$(VENV)' ]; then \
		make install; \
	fi
	@echo "$(CYAN)Note:$(BOLD) PUDB defaults itself to your initial ~/.config/pudb/pudb.cfg theme."
	@echo "$(BOLD)If it is your first time running PUDB, it will be that ugly blue theme.$(RESET)"
	@echo "$(BOLD)You can change the theme by pressing CTRL + P in the debugger.$(RESET)"
	@echo "$(GREY)Tip: Monokai/Mono & Dark Vim support your terminal's opacity and default themselves to your original terminal theme.$(RESET)"
	@echo "$(BOLD)$(VENV)/bin/$(PY) -m pdub src/main.py$(RESET)"
	@sleep 1;
	@clear;
	$(VENV)/bin/$(PY) -m pudb 'src/main.py' 2>/dev/null

lint:
	@if [ ! -d '$(VENV)' ]; then \
		make install; \
	fi; \
	$(VENV)/bin/flake8 'src'; \
	$(VENV)/bin/mypy 'src'; \

lint-strict:
	@if [ ! -d $(VENV) ]; then \
		make install; \
	fi; \
	$(VENV)/bin/flake8 'src' --select=F; \
	$(VENV)/bin/mypy 'src' --strict; \

clean:
	rm -rf $(VENV)
	find . -name "*.pyc" -exec rm -f {} \;
	find . -name "*.pyo" -exec rm -f {} \;
	find . -type d -name "__pycache__" -exec rm -rf {} \;
	@find . -type d -name ".mypy_cache" 2>>/dev/null -exec rm -rf {} \;

.PHONY: help run install clean lint lint-strict

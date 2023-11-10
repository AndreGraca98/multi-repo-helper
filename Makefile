.SILENT: ;

setup:
	echo 'Please specify a shellrc file to setup mrh. For example: make setup-bash or make setup-zsh'

setup-bash: ## Setup mrh for bash
	SHELLRC_FILE=~/.bash_profile COMPLETION_FILE=~/.bash_completion python _setup.py

setup-zsh: ## Setup mrh for zsh
	SHELLRC_FILE=~/.zshrc COMPLETION_FILE=~/.zshrc python _setup.py

test: ## Run tests
	pytest

lint: ## Run linters
	pre-commit run -a

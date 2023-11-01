.SILENT: ;

setup: 
	echo 'Please specify a shellrc file to setup mrh. For example: make setup-bash or make setup-zsh'

setup-bash: ## Setup mrh for bash
	SHELLRC_FILE=~/.bashrc python setup.py
	
setup-zsh: ## Setup mrh for zsh
	SHELLRC_FILE=~/.zshrc python setup.py
	
.ONESHELL:
VENV_NAME=.venv
PYTHON=python3
PIP=$(VENV_NAME)/bin/pip
SRC=src

.PHONY: virtualenv install run debug lint format test

virtualenv:
	@echo "Creating virtualenv ..."
	@rm -rf $(VENV_NAME)
	@$(PYTHON) -m venv $(VENV_NAME)
	@$(PIP) install -U pip
	@echo "Virtual environment created."
	@make install

install:
	@echo "Installing dependencies ..."
	@$(PIP) install -r requirements.txt
	@echo "Dependencies installed."
	@echo "!!!Activate the virtual environment by running: source $(VENV_NAME)/bin/activate"

run:
	@echo "Running main.py"
	@$(PYTHON) $(SRC)/main.py $(ARGS)

start-server:
	@echo "Starting Flask app with Gunicorn..."
	@$(VENV_NAME)/bin/gunicorn -w 4 -b 0.0.0.0:5000 --timeout 2000 --log-level debug $(SRC).app:app
	@echo "Server started. Use jobs to manage background processes."


debug:
	@echo "Debugging the application using $(PYTHON) ..."
	@$(PYTHON) -m pudb $(SRC)/main.py $(ARGS)
	@echo "Debugging stopped."

lint:
	@echo "Linting the code ..."
	@$(VENV_NAME)/bin/flake8 $(SRC)
	@find $(SRC) -name '*.py' -exec echo Linting {} \; -exec $(VENV_NAME)/bin/flake8 {} \;
	@echo "Code linting completed."

format:
	@echo "Formatting the code ..."
	@$(VENV_NAME)/bin/black $(SRC)
	@echo "Code formatting completed."

test:
	@echo "Running the tests with coverage ..."
	@$(VENV_NAME)/bin/pytest
	@echo "Tests run."
	
ctags:
	@echo "Generating CTags for the project ..."
	@ctags -R --languages=Python --python-kinds=-i $(SRC)
	@echo "CTags generated successfully."
.PHONY: test flake clean install

all: test flake

test:
	pytest --cov-report term-missing --cov=cache --cov=stream --verbose tests/

flake:
	@echo 'flak8 output:'
	@flake8 . || true

clean:
	@echo "Removing cache directories"
	@find . -name __pycache__ -type d -exec rm -rf {} +
	@find . -name .cache -type d -exec rm -rf {} +
	@find . -name .coverage -delete

install:
	pip install -r requirements.txt
	pip install -r requirements_test.txt
	pip install -r requirements_app.txt

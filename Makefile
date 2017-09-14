.PHONY: test flake clean

all: test flake

test:
	pytest --cov-report term-missing --cov=cache --verbose tests/

flake:
	@echo 'flak8 output:'
	@flake8 . || true

clean:
	@echo "Removing .pyc cache files"
	@find . -name "*.pyc" -delete
	@find . -name "_pycache_" -rmdir
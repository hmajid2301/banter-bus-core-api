.DEFAULT_GOAL := help


.PHONY: help
help: ## Generates a help README
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: start
start:
	@docker-compose up --build -d


.PHONY: start-deps
start-deps:
	@docker-compose up --build -d database database-gui

.PHONY: unit_tests
unit_tests:
	@tox -e py39


.PHONY: integration_tests
integration_tests:
	@tox -e integration


.PHONY: coverage
coverage:
	@tox -e coverage


.PHONY: install-venv
install-venv:
	@tox -e dev


.PHONY: install-hooks
install-hooks:
	@tox -e pre-commit -- install


.PHONY: lint
lint:
	@tox -e pre-commit -- run --all-files


.PHONY: install-dev
install-dev:
	@pip install -e .


.PHONY: build-package
build-package:
	@python setup.py sdist


.PHONY: clean
clean:
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' | xargs rm -rf
	@find . -type d -name '*.ropeproject' | xargs rm -rf
	@rm -rf build/
	@rm -rf dist/
	@rm -f src/*.egg
	@rm -f src/*.eggs
	@rm -rf src/*.egg-info/
	@rm -f MANIFEST
	@rm -rf docs/build/
	@rm -rf htmlcov/
	@rm -f .coverage
	@rm -f .coverage.*
	@rm -rf .cache/
	@rm -f coverage.xml
	@rm -f *.cover
	@rm -rf .pytest_cache/
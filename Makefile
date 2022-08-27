.DEFAULT_GOAL := help

# TODO: tidy this up

.PHONY: help
help: ## Generates a help README
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: start
start: ## Start the application "stack" using Docker
	@docker compose up --build

.PHONY: build
build: ## Build all the docker images
	@docker compose build

.PHONY: start-deps
start-deps: ## Start all the Docker containers that this app depends on directly
	@docker compose pull
	@docker compose up --build -d database database-gui database-seed message-queue management-api

.PHONY: lint
lint: build ## Run the lint steps (pre-commit hook) in docker
	@docker compose run --rm --no-deps app make _lint

.PHONY: unit_tests
unit_tests: build ## Run all the unit tests in docker
	@docker compose run --rm --no-deps app make _unit_tests

.PHONY: integration_tests
integration_tests: build ## Run all the integration tests in docker
	@docker compose run --rm app make _integration_tests

.PHONY: contract_tests
contract_tests: build ## Create contract test JSON in docker
	@docker compose run --rm --no-deps  app make _contract_tests

.PHONY: coverage
coverage: build ## Run the integration tests with code coverage report generated in docker
	@docker compose run --rm app make _coverage

.PHONY: _unit_tests
_unit_tests: ## Run all the unit tests
	@poetry run pytest -v tests/unit

.PHONY: _integration_tests
_integration_tests: ## Run all the integration tests
	@poetry run pytest -v tests/integration

.PHONY: _contract_tests
_contract_tests: ## Create contract test JSON
	@poetry run pytest -v tests/contract

.PHONY: _coverage
_coverage: ## Run the integration tests with code coverage report generated
	@poetry run pytest -v --junitxml=report.xml --cov=app/ tests/integration
	@poetry run coverage xml

.PHONY: _lint
_lint: ## Run the lint steps (pre-commit hook)
	@poetry run pre-commit run --all-files

.PHONY: pull-template-updates
pull-template-updates: ## Pull updates from upstream template
	@poetry run copier update

.PHONY: clean
clean: ### Clean all temporary files
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
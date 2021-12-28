.DEFAULT_GOAL := help


.PHONY: help
help: ## Generates a help README
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: start
start:
	@docker-compose up --build -d


.PHONY: start-deps
start-deps:
	@docker-compose pull
	@docker-compose up --build -d database database-gui database-seed management-api


.PHONY: unit_tests_docker
unit_tests_docker:
	@docker-compose run app make unit_tests


.PHONY: integration_tests_docker
integration_tests_docker:
	@docker-compose run app make integration_tests


.PHONY: coverage_docker
coverage_docker:
	@docker-compose run app make coverage


.PHONY: unit_tests
unit_tests:
	@poetry run pytest -v tests/unit


.PHONY: integration_tests
integration_tests:
	@poetry run pytest -v tests/integration


.PHONY: contract_tests
contract_tests:
	@poetry run pytest -v tests/contract


.PHONY: coverage
coverage:
	@poetry run pytest -v --junitxml=report.xml --cov=app/ tests/integration
	@poetry run coverage xml


.PHONY: install-hooks
install-hooks:
	@poetry pre-commit install


.PHONY: lint
lint:
	@poetry run pre-commit run --all-files


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
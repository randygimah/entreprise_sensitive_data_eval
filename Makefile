.PHONY: lint format type-check test clean install-dev

install-dev:
	pip install -r requirements.txt

format:
	black sensitive_eval/
	isort sensitive_eval/

lint:
	flake8 sensitive_eval/
	isort --check-only --diff sensitive_eval/

type-check:
	mypy sensitive_eval/

test:
	pytest --tb=short 

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# Run all checks
check: format lint type-check test

# Setup development environment
setup: install-dev
	pre-commit install  # if pre-commit is added later
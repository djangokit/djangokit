.PHONY = test
test:
	DOTENV_FILE=src/djangokit/core/test/.env.test \
	  poetry run pytest -rA --doctest-modules --disable-warnings

.PHONY = test-cov
test-cov:
	DOTENV_FILE=src/djangokit/core/test/.env.test \
	  poetry run pytest -rA --doctest-modules --disable-warnings --cov=djangokit.core

.PHONY = tox
tox:
	poetry run tox

.PHONY = clean-tox
clean-tox:
	rm -rf .tox
	poetry run tox

.PHONY = check
check:
	poetry run black --check .
	poetry run isort --check --profile black .
	poetry run ruff .
	poetry run mypy

.PHONY = format
format:
	poetry run black .
	poetry run isort --profile black .

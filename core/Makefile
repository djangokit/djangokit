.PHONY = test
test:
	DJANGO_SETTINGS_MODULE=djangokit.core.test.settings \
	  poetry run pytest -rA --doctest-modules --disable-warnings

.PHONY = check
check:
	black --check .
	isort --check --profile black .
	mypy

.PHONY = format
format:
	poetry run black .
	poetry run isort --profile black .

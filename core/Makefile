.PHONY = test
test:
	DJANGO_SETTINGS_MODULE=djangokit.core.settings \
	  DJANGO_TEST=true \
	  DJANGOKIT_PACKAGE="djangokit.core.test" \
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

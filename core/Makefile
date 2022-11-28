.PHONY = test
test:
	DJANGO_SETTINGS_MODULE=djangokit.core.settings \
	  DJANGO_TEST=true \
	  DJANGOKIT_PACKAGE=djangokit.core.test \
	  poetry run pytest -rA --doctest-modules --disable-warnings

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
	poetry run mypy

.PHONY = format
format:
	poetry run black .
	poetry run isort --profile black .

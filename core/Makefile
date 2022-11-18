.PHONY = test
test:
	DJANGO_SETTINGS_MODULE=djangokit.core.test.settings \
	  poetry run pytest -rA --doctest-modules --disable-warnings

.PHONY = format
format:
	poetry run black .
	poetry run isort --profile black .

django_secret_key = TEST-SECRET-KEY-$(shell LC_ALL=C tr -dc A-Za-z0-9 </dev/urandom | head -c 16)
django_api_key = TEST-API-KEY-$(shell LC_ALL=C tr -dc A-Za-z0-9 </dev/urandom | head -c 16)

.PHONY = test
test:
	DJANGO_SETTINGS_FILE=src/djangokit/core/test/settings.test.toml \
	  DJANGO_SECRET_KEY=$(django_secret_key) \
	  DJANGO_API_KEY=$(django_api_key) \
	  poetry run pytest -rA --disable-warnings

.PHONY = test-cov
test-cov:
	DJANGO_SETTINGS_FILE=src/djangokit/core/test/settings.test.toml \
	  DJANGO_SECRET_KEY=$(django_secret_key) \
	  DJANGO_API_KEY=$(django_api_key) \
	  poetry run pytest -rA --disable-warnings --cov=djangokit.core

.PHONY = tox
tox:
	poetry run tox

.PHONY = clean-tox
clean-tox:
	rm -rf .tox
	poetry run tox

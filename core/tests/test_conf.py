import os

import djangokit.core.test
from django.conf import settings
from django.test import SimpleTestCase


class TestConf(SimpleTestCase):
    def test_DJANGO_SETTINGS_FILE(self):
        file = os.environ["DJANGO_SETTINGS_FILE"]
        file = os.path.abspath(file)
        expected = os.path.join(djangokit.core.test.__path__[0], "settings.test.toml")
        self.assertEqual(file, expected)

    def test_ENV(self):
        self.assertEqual(settings.ENV, "test")

    def test_SECRET_KEY(self):
        self.assertTrue(settings.SECRET_KEY)
        self.assertTrue(settings.SECRET_KEY.startswith("TEST-SECRET-KEY-"))

    def test_API_KEY(self):
        # API.KEY is set from env
        self.assertTrue(settings.API)
        self.assertTrue(settings.API["KEY"])
        self.assertTrue(settings.API["KEY"].startswith("TEST-API-KEY-"))

    def test_SOME_SETTING(self):
        # SOME_SETTING can be set from env but uses a default from the
        # settings file
        self.assertTrue(settings.SOME_SETTING)
        self.assertEqual(settings.SOME_SETTING, "some setting")

    def test_get_known_setting(self):
        package = settings.DJANGOKIT.package
        self.assertEqual(package, "djangokit.core.test")

    def test_get_unknown_setting(self):
        with self.assertRaises(AttributeError):
            settings.DJANGOKIT.unknown

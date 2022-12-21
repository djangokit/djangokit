import os

from django.conf import settings
from django.test import SimpleTestCase

import djangokit.core.test


class TestConf(SimpleTestCase):
    def test_ENV(self):
        env = os.environ["ENV"]
        self.assertEqual(env, "test")

    def test_DOTENV_FILE(self):
        dotenv_file = os.environ["DOTENV_FILE"]
        dotenv_file = os.path.abspath(dotenv_file)
        expected = os.path.join(djangokit.core.test.__path__[0], ".env.test")
        self.assertEqual(dotenv_file, expected)

    def test_TEST(self):
        self.assertTrue(settings.TEST)

    def test_get_known_setting(self):
        package = settings.DJANGOKIT.package
        self.assertEqual(package, "djangokit.core.test")

    def test_get_unknown_setting(self):
        with self.assertRaises(AttributeError):
            settings.DJANGOKIT.unknown

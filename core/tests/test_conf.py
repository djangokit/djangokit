from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from djangokit.core import conf


class TestConf(SimpleTestCase):
    def test_get_known_setting(self):
        package = conf.settings.package
        self.assertEqual(package, "djangokit.core.test")

    def test_get_unknown_setting(self):
        with self.assertRaises(AttributeError):
            conf.settings.unknown

    def test_get_setting_with_incorrect_type(self):
        del conf.settings.package
        with self.settings(DJANGOKIT={"package": 1}):
            self.assertEqual(settings.DJANGOKIT["package"], 1)
            with self.assertRaises(ImproperlyConfigured):
                conf.settings.package

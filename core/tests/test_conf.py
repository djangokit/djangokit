from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from djangokit.core import conf


class TestConf(SimpleTestCase):
    def test_get_known_setting(self):
        package = conf.get_setting("package")
        self.assertEqual(package, "djangokit.core.test")

    def test_get_unknown_setting(self):
        self.assertRaises(LookupError, conf.get_setting, "unknown")

    def test_get_setting_with_incorrect_type(self):
        conf.get_setting.cache_clear()
        with self.settings(DJANGOKIT={"package": 1}):
            self.assertRaises(ImproperlyConfigured, conf.get_setting, "package")

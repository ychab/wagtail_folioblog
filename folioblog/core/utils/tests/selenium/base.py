import sys
import unittest

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from django.test.selenium import SeleniumTestCase, SeleniumTestCaseBase

from wagtail.models import Locale, Site

from wagtail_factories import SiteFactory


def skip_mobile(msg=""):
    """
    Decorator to skip test method with mobile testcase.
    """

    def _skip_mobile(func):
        func.skip_mobile_reason = msg or "Mobile skip"
        return func

    return _skip_mobile


class MetaSeleniumTestCase(SeleniumTestCaseBase):
    """
    Yeah baby, this is where the dark magic happen...
    In 6 months, I'll probably kill myself for this!!
    """

    def __new__(cls, name, bases, attrs):
        test_class = super().__new__(cls, name, bases, attrs)

        # Skip base classes (no test methods except mobile which inherit)
        has_tests = any([attr for attr in attrs if attr.startswith("test_")])
        if not has_tests and not test_class.is_mobile:
            return test_class

        # Duplicate testcase for mobile version
        if test_class.has_mobile:
            # Create the derivated mobile class test case
            module = sys.modules[test_class.__module__]
            mobile_test_class = cls.__new__(
                cls,
                "%s%s" % ("Mobile", name),
                (test_class,),
                {
                    "has_mobile": False,
                    "is_mobile": True,  # but enable it for child mobile class
                    "__module__": test_class.__module__,
                },
            )

            # Tag it as mobile to filter on it
            tags = getattr(test_class, "tags", set())
            tags = tags.copy()
            tags.add("mobile")
            mobile_test_class = tag(*tags)(mobile_test_class)

            # Then attach it to its python module.
            setattr(module, mobile_test_class.__name__, mobile_test_class)

        elif test_class.is_mobile:  # pragma: no branch
            # For mobile, skip some useless tests thanks to skip_mobile decorator.
            for func_name in dir(test_class):
                if not func_name.startswith("test_"):
                    continue
                func = getattr(test_class, func_name)
                skip_reason = getattr(func, "skip_mobile_reason", None)
                if skip_reason:
                    setattr(test_class, func_name, unittest.skip(skip_reason)(func))

        return test_class

    def create_options(self):
        options = super().create_options()

        if self.browser in ["chrome", "chromium"]:  # pragma: no branch
            # Without some of those options, it could be VERY VERY slow!!
            option_args = [
                "--disable-gpu",
                "--ignore-certificate-errors",
                "--disable-extensions",
                "--no-sandbox",  # Obviously, required if run as root
                "--disable-dev-shm-usage",
                "--headless",  # Required since chromedriver 118?
            ]
            for option in option_args:
                options.add_argument(option)

        return options


@tag("selenium", "slow")
class FolioBlogSeleniumServerTestCase(SeleniumTestCase, StaticLiveServerTestCase, metaclass=MetaSeleniumTestCase):
    # Mixin implicit and explicit wait is not recommended:
    # @see https://www.selenium.dev/documentation/webdriver/waits/#implicit-wait
    implicit_wait = 0

    browser = "chrome"

    has_mobile = True  # Should it have a child mobile testcase?
    is_mobile = False

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        if cls.is_mobile:
            if cls.browser in ["chrome", "chromium"]:  # pragma: no branch
                # Without this emulation, mobile mode is not on...!
                cls.selenium.execute_cdp_cmd(
                    "Emulation.setDeviceMetricsOverride",
                    {
                        "width": 360,
                        "height": 780,
                        "deviceScaleFactor": 46,
                        "mobile": True,
                    },
                )
            cls.selenium.set_window_size("360", "780")
        else:
            cls.selenium.set_window_size("1920", "1200")

        # Not necessary required, but could avoid some side effect?
        cls.selenium.maximize_window()

    @classmethod
    def tearDownClass(cls):
        # @see SeleniumTestCase._tearDownClassInternal()
        if hasattr(cls, "selenium"):  # pragma: no branch
            cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        super().setUp()

        # Be sure local exists (i.e: not after first flush)
        Locale.objects.get_or_create(language_code=settings.LANGUAGE_CODE)

        # Delete initial migration data site if any (i.e: before first flush).
        Site.objects.all().delete()
        # Then create a site with live server url.
        self.site = SiteFactory(
            hostname=self.host,
            port=self.server_thread.port,
            is_default_site=True,
        )

from django.test import TestCase

from wagtail.models import Site


class SiteRootPageSwitchTestCase(TestCase):
    site = None
    root_page = None

    @classmethod
    def setUpTestData(cls):
        cls.site.root_page = cls.root_page
        cls.site.save()

    @classmethod
    def tearDownClass(cls):
        # First let's Django rollback all DB operations during test class.
        super().tearDownClass()
        # THEN clear site root path cache! Take me a while before found it!
        Site.clear_site_root_paths_cache()

from django.test import TestCase
from django.urls import reverse

from wagtail.models import Site

from wagtail_factories import SiteFactory

from folioblog.core.factories import MenuFactory
from folioblog.user.factories import UserFactory


class MenuSnippetViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)
        cls.admin = UserFactory(is_superuser=True)

        cls.menu1 = MenuFactory(site=cls.site)
        cls.menu2 = MenuFactory(site=SiteFactory())

        cls.url = reverse("wagtailsnippets_core_menu:list")

    def test_filter_site_none(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertIn(self.menu1, list(response.context_data["object_list"]))
        self.assertIn(self.menu2, list(response.context_data["object_list"]))

    def test_filter_site(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url, data={"site": self.site.pk})
        self.assertEqual(response.status_code, 200)

        self.assertIn(self.menu1, list(response.context_data["object_list"]))
        self.assertNotIn(self.menu2, list(response.context_data["object_list"]))

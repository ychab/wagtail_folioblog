from django.test import TestCase
from django.urls import reverse

from wagtail.models import Site

from wagtail_factories import SiteFactory

from folioblog.user.factories import UserFactory
from folioblog.video.factories import VideoCategoryFactory


class VideoCategoryChooserViewSetTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)
        cls.admin = UserFactory(is_superuser=True)

        cls.cat1 = VideoCategoryFactory(site=cls.site)
        cls.cat2 = VideoCategoryFactory(site=SiteFactory())

        cls.url = reverse("videocategory_chooser:choose_results")

    def test_filter_site_none(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertIn(self.cat1, response.context_data["results"].object_list)
        self.assertIn(self.cat2, response.context_data["results"].object_list)

    def test_filter_site(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url, data={"site": self.site.pk})
        self.assertEqual(response.status_code, 200)

        self.assertIn(self.cat1, response.context_data["results"].object_list)
        self.assertNotIn(self.cat2, response.context_data["results"].object_list)


class VideoCategorySnippetViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)
        cls.admin = UserFactory(is_superuser=True)

        cls.cat1 = VideoCategoryFactory(site=cls.site)
        cls.cat2 = VideoCategoryFactory(site=SiteFactory())

        cls.url = reverse("wagtailsnippets_video_videocategory:list")

    def test_filter_site_none(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertIn(self.cat1, list(response.context_data["object_list"]))
        self.assertIn(self.cat2, list(response.context_data["object_list"]))

    def test_filter_site(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url, data={"site": self.site.pk})
        self.assertEqual(response.status_code, 200)

        self.assertIn(self.cat1, list(response.context_data["object_list"]))
        self.assertNotIn(self.cat2, list(response.context_data["object_list"]))

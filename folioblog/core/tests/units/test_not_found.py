from html import unescape

from django.test import TestCase
from django.urls import reverse

from wagtail.models import Site

from folioblog.core.factories import ImageFactory
from folioblog.home.factories import HomePageFactory


class NotFoundPageTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        HomePageFactory(parent=site.root_page)  # for link bellow
        cls.url = reverse('404')

    def test_404_image(self):
        image_bg = ImageFactory(title='404-bg')
        rendition_bg = image_bg.get_rendition('fill-1905x560')
        image_body = ImageFactory(title='404-body')
        rendition_body = image_body.get_rendition('width-700')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
        html = unescape(response.content.decode())

        self.assertIn(rendition_bg.url, html)
        self.assertIn(rendition_body.url, html)

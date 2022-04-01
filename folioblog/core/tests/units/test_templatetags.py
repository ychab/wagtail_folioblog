import os
from html import unescape

from django.test import TestCase

from wagtail.models import Site

from folioblog.core.factories import BasicPageFactory, ImageFactory
from folioblog.core.factories.images import PhotographerFactory


class PhotoCreditTemplateTagTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)

    def test_page_image_with_credit_link(self):
        photographer = PhotographerFactory()
        image = ImageFactory(photographer=photographer)
        page = BasicPageFactory(parent=self.site.root_page, image=image)

        response = self.client.get(page.url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn(photographer.name, html)
        self.assertIn(f'<a href="{photographer.website}"', html)

    def test_page_image_with_credit(self):
        photographer = PhotographerFactory(website=None)
        image = ImageFactory(photographer=photographer)
        page = BasicPageFactory(parent=self.site.root_page, image=image)

        response = self.client.get(page.url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn(photographer.name, html)

    def test_page_image_without_credit(self):
        image = ImageFactory(photographer=None)
        page = BasicPageFactory(parent=self.site.root_page, image=image)

        response = self.client.get(page.url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn(os.path.basename(image.file.name), html)

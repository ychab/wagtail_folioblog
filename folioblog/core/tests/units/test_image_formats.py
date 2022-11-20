from html import unescape

from django.test import TestCase
from django.utils.translation import get_language, to_locale

from wagtail.models import Site
from wagtail.rich_text import RichText

from faker import Faker

from folioblog.core.factories import BasicPageFactory, ImageFactory

current_locale = to_locale(get_language())
fake = Faker(locale=current_locale)


class BodyFullImageFormatTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)

        cls.image = ImageFactory()
        cls.rendition = cls.image.get_rendition('width-940')

        text = fake.text()
        text += f'<embed alt="Test text alt" embedtype="image" format="bodyfullfuild" id="{cls.image.pk}"/>'

        cls.page = BasicPageFactory(parent=cls.site.root_page, body=RichText(text))

    def test_image_src(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn(self.rendition.url, html)

    def test_image_caption(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn('<figcaption class="caption figure-caption">Test text alt</figcaption>', html)


class CreditLightboxImageFormatTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)

        cls.image = ImageFactory()
        cls.rendition = cls.image.get_rendition('width-940')

        alt_text = 'Test text alt'
        cls.alt_text_html = unescape(cls.image.figcaption(alt_text))

        text = fake.text()
        text += f'<embed alt="{alt_text}" embedtype="image" format="creditlightbox" id="{cls.image.pk}"/>'

        cls.page = BasicPageFactory(parent=cls.site.root_page, body=RichText(text))

    def test_image_src(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn(self.rendition.url, html)

    def test_image_figcaption(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn(f'<figcaption class="caption figure-caption">{self.alt_text_html}</figcaption>', html)

    def test_image_lightbox(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn(f'<div class="glightbox-desc custom-desc-{self.image.pk}">{self.alt_text_html}</div>', html)

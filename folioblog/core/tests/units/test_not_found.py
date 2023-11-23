from html import unescape

from django.test import TestCase
from django.urls import reverse
from django.utils import translation

from wagtail.models import Site

from folioblog.core.factories import (
    FolioBlogSettingsFactory,
    ImageFactory,
    LocaleFactory,
    MenuFactory,
)
from folioblog.home.factories import HomePageFactory


class NotFoundPageTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)
        cls.locale_en = LocaleFactory(language_code="en")

        cls.homepage_fr = HomePageFactory(parent=cls.site.root_page)
        cls.homepage_en = cls.homepage_fr.copy_for_translation(
            locale=cls.locale_en,
            copy_parents=True,
        )
        cls.menu_fr = MenuFactory(site=cls.site, homepage=cls.homepage_fr)
        cls.menu_en = cls.menu_fr.copy_for_translation(
            locale=cls.locale_en,
            exclude_fields=["homepage"],
        )
        cls.menu_en.homepage = cls.homepage_en
        cls.menu_en.save()

        cls.image = ImageFactory()

        # Create site settings if not exist yet
        FolioBlogSettingsFactory(site=cls.site)
        cls.site.refresh_from_db()

        # Then update it.
        settings_factory = FolioBlogSettingsFactory.build(
            text_404__0__items__language="fr",
            text_404__0__items__title="Page vraiment introuvable",
            text_404__0__items__subtitle="Aïe",
            text_404__0__items__text="Essaye encore !",
            text_404__0__items__link_text="Retour à la maison !",
            text_404__1__items__language="en",
            text_404__1__items__title="Page really not found",
            text_404__1__items__subtitle="Aouch",
            text_404__1__items__text="Try again!",
            text_404__1__items__link_text="Back to home!",
        )
        cls.site.folioblogsettings.image_404 = cls.image
        cls.site.folioblogsettings.text_404 = settings_factory.text_404
        cls.site.folioblogsettings.save()

        cls.settings_fr = cls.site.folioblogsettings.text_404[0].value
        cls.settings_en = cls.site.folioblogsettings.text_404[1].value

    def test_404_image(self):
        rendition_bg = self.image.get_rendition("fill-1905x560")

        url = reverse("404")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        html = unescape(response.content.decode())

        self.assertIn(rendition_bg.url, html)

    def test_404_fr(self):
        with translation.override("fr"):
            url = reverse("404")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        html = unescape(response.content.decode())

        self.assertIn(self.settings_fr["title"], html)
        self.assertIn(self.settings_fr["subtitle"], html)
        self.assertIn(self.settings_fr["text"], html)
        self.assertIn(self.settings_fr["link_text"], html)

    def test_404_en(self):
        with translation.override("en"):
            url = reverse("404")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        html = unescape(response.content.decode())

        self.assertIn(self.settings_en["title"], html)
        self.assertIn(self.settings_en["subtitle"], html)
        self.assertIn(self.settings_en["text"], html)
        self.assertIn(self.settings_en["link_text"], html)

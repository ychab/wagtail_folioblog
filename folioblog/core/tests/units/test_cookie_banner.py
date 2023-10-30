from html import unescape

from django.test import TestCase

from wagtail.models import Site

from folioblog.core.factories import (
    BasicPageFactory,
    FolioBlogSettingsFactory,
    LocaleFactory,
)


class CookieBannerSettingsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = Site.objects.get(is_default_site=True)

        # Create site settings if not exist yet
        FolioBlogSettingsFactory(site=cls.site)
        cls.site.refresh_from_db()

        # Then update it.
        settings_factory = FolioBlogSettingsFactory.build(
            cookie_banner__0__banners__language="fr",
            cookie_banner__0__banners__title="Coucou toi",
            cookie_banner__1__banners__language="en",
            cookie_banner__1__banners__title="Hello Honey",
        )
        cls.site.folioblogsettings.cookie_banner = settings_factory.cookie_banner
        cls.site.folioblogsettings.save()

        cls.settings_fr = cls.site.folioblogsettings.cookie_banner[0].value
        cls.settings_en = cls.site.folioblogsettings.cookie_banner[1].value

        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.page_fr = BasicPageFactory(
            parent=cls.site.root_page,
            locale=LocaleFactory(language_code="fr"),
        )
        cls.page_en = cls.page_fr.copy_for_translation(
            locale=LocaleFactory(language_code="en"),
            copy_parents=True,
            alias=True,
        )

    def test_cookie_banner_fr(self):
        response = self.client.get(self.page_fr.full_url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn(self.settings_fr["title"], html)
        self.assertIn(self.settings_fr["text"], html)
        self.assertIn(self.settings_fr["page"].url_path, html)
        self.assertIn(self.settings_fr["link_text"], html)
        self.assertIn(self.settings_fr["button_cancel_text"], html)
        self.assertIn(self.settings_fr["button_accept_text"], html)

    def test_cookie_banner_en(self):
        response = self.client.get(self.page_en.full_url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn(self.settings_en["title"], html)
        self.assertIn(self.settings_en["text"], html)
        self.assertIn(self.settings_en["page"].url_path, html)
        self.assertIn(self.settings_en["link_text"], html)
        self.assertIn(self.settings_en["button_cancel_text"], html)
        self.assertIn(self.settings_en["button_accept_text"], html)

from django.test import TestCase

from wagtail.models import Site

from wagtail_factories import PageFactory, SiteFactory

from folioblog.blog.factories import BlogIndexPageFactory
from folioblog.core.factories import LocaleFactory
from folioblog.core.factories.snippets import MenuFactory, MenuLinkFactory
from folioblog.core.models import Menu


class MenuTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        cls.index = BlogIndexPageFactory(parent=site.root_page)

    def tearDown(self):
        Menu.objects.all().delete()

    def test_menu_links(self):
        menu = MenuFactory(links__number=3)

        response = self.client.get(self.index.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context["menu_homepage"], menu.homepage)

        for link in menu.links.all():
            self.assertIn(
                link.related_page.slug,
                response.context["menu_links"],
                msg=f"Checking for link {link.pk}",
            )

    def test_menu_inactive(self):
        MenuFactory(is_active=False, links__number=3)

        response = self.client.get(self.index.url)
        self.assertEqual(response.status_code, 200)

        self.assertFalse(response.context["menu_homepage"])
        self.assertFalse(response.context["menu_links"])

    def test_menu_links_not_live(self):
        menu = MenuFactory(links__number=3)
        page = PageFactory(live=False)
        link = MenuLinkFactory(menu=menu, related_page=page)
        menu.links.add(link)
        self.assertEqual(menu.links.count(), 4)

        response = self.client.get(self.index.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["menu_links"]), 3)


class MenuI18nTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        locale_fr = LocaleFactory(language_code="fr")
        locale_en = LocaleFactory(language_code="en")

        site = Site.objects.get(is_default_site=True)
        cls.index_fr = BlogIndexPageFactory(parent=site.root_page, locale=locale_fr)
        cls.index_en = cls.index_fr.copy_for_translation(
            locale=locale_en,
            copy_parents=True,
            alias=True,
        )

        cls.menu_fr = MenuFactory(
            locale=locale_fr, homepage=PageFactory(locale=locale_fr)
        )
        cls.menu_en = cls.menu_fr.copy_for_translation(locale=locale_en)
        cls.menu_en.homepage = PageFactory(locale=locale_en)
        cls.menu_en.save()

    def test_menu_fr(self):
        response = self.client.get(self.index_fr.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["menu_homepage"], self.menu_fr.homepage)

    def test_menu_en(self):
        response = self.client.get(self.index_en.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["menu_homepage"], self.menu_en.homepage)


class MenuMultiDomainTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_page = BlogIndexPageFactory(slug="blog")
        cls.index_other = BlogIndexPageFactory(slug="blog-other")

        cls.site = Site.objects.get(is_default_site=True)
        cls.site_other = SiteFactory(root_page=cls.index_other)

        cls.menu = MenuFactory(homepage=cls.root_page, site=cls.site)
        cls.menu_other = MenuFactory(homepage=cls.index_other, site=cls.site_other)

    def test_menu_filter_site(self):
        response = self.client.get(self.root_page.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(self.root_page, response.context["menu_homepage"].specific)
        self.assertNotEqual(
            self.index_other, response.context["menu_homepage"].specific
        )

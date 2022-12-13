from django.test import TestCase

from wagtail.models import Site

from wagtail_factories import PageFactory

from folioblog.blog.factories import BlogIndexPageFactory
from folioblog.core.factories import LocaleFactory
from folioblog.core.factories.snippets import MenuFactory, MenuLinkFactory


class MenuTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        cls.menu = MenuFactory(links__number=3)
        cls.index = BlogIndexPageFactory(parent=site.root_page)

    def test_menu_links(self):
        response = self.client.get(self.index.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['menu_homepage'], self.menu.homepage)

        for link in self.menu.links.all():
            self.assertIn(
                link.related_page.slug,
                response.context['menu_links'],
                msg=f'Checking for link {link.pk}',
            )

    def test_menu_links_not_live(self):
        page = PageFactory(live=False)
        link = MenuLinkFactory(menu=self.menu, related_page=page)
        self.menu.links.add(link)
        self.assertEqual(self.menu.links.count(), 4)

        response = self.client.get(self.index.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['menu_links']), 3)

        self.menu.links.remove(link)


class MenuI18nTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        locale_fr = LocaleFactory(language_code='fr')
        locale_en = LocaleFactory(language_code='en')

        site = Site.objects.get(is_default_site=True)
        cls.index_fr = BlogIndexPageFactory(
            parent=site.root_page,
            locale=locale_fr
        )
        cls.index_en = cls.index_fr.copy_for_translation(
            locale=locale_en,
            copy_parents=True,
            alias=True,
        )

        cls.menu_fr = MenuFactory(locale=locale_fr, homepage=PageFactory(locale=locale_fr))
        cls.menu_en = cls.menu_fr.copy_for_translation(locale=locale_en)
        cls.menu_en.homepage = PageFactory(locale=locale_en)
        cls.menu_en.save()

    def test_menu_fr(self):
        response = self.client.get(self.index_fr.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['menu_homepage'], self.menu_fr.homepage)

    def test_menu_en(self):
        response = self.client.get(self.index_en.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['menu_homepage'], self.menu_en.homepage)

from django.test import TestCase

from wagtail_factories import PageFactory, SiteFactory

from folioblog.core.factories import MenuFactory


class MenuFactoryTestCase(TestCase):
    def test_links_site(self):
        home = PageFactory(slug="foo")
        site = SiteFactory(site_name="foo", root_page=home)

        home_other = PageFactory(slug="bar")
        site_other = SiteFactory(site_name="bar", root_page=home_other)

        menu = MenuFactory(homepage=home, site=site, links__number=1)
        menu_other = MenuFactory(homepage=home_other, site=site_other, links__number=1)

        self.assertEqual(menu.links.first().related_page.get_root(), home)
        self.assertNotEqual(menu.links.first().related_page.get_root(), home_other)

        self.assertEqual(menu_other.links.first().related_page.get_root(), home_other)
        self.assertNotEqual(menu_other.links.first().related_page.get_root(), home)

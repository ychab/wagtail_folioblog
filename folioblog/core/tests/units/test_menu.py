from django.test import TestCase

from wagtail.models import Site

from folioblog.blog.factories import BlogIndexPageFactory
from folioblog.core.factories.snippets import MenuFactory


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

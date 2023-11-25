from django.test import TestCase

from wagtail_factories import SiteFactory

from folioblog.blog.factories import BlogIndexPageFactory, BlogPageFactory
from folioblog.home.factories import HomePageFactory


class BlogPageFactoryTestCase(TestCase):
    def test_other_site(self):
        home = HomePageFactory(parent=None)
        site = SiteFactory(root_page=home)

        blog_index = BlogIndexPageFactory(parent=home)
        blog_post = BlogPageFactory(
            parent=blog_index,
            tags__number=1,
            related_pages__number=1,
            promoted=True,
        )

        self.assertEqual(blog_post.category.site, site)
        self.assertEqual(blog_post.tags.first().site, site)
        self.assertEqual(blog_post.related_links.first().related_page.get_site(), site)
        self.assertEqual(blog_post.promoted_links.first().snippet.site, site)

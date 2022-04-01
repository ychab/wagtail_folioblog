from django.test import TestCase

from folioblog.blog.factories import BlogCategoryFactory


class BlogCategoryModelTestCase(TestCase):

    def test_slug_auto(self):
        cat = BlogCategoryFactory(name='Foo Bar Baz', slug=None)
        cat.refresh_from_db()
        self.assertEqual(cat.slug, 'foo-bar-baz')

    def test_slug_manual(self):
        cat = BlogCategoryFactory(name='foo', slug='baz')
        cat.refresh_from_db()
        self.assertEqual(cat.slug, 'baz')

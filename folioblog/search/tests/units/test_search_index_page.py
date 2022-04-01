from html import unescape

from django.test import TestCase, override_settings
from django.utils.html import escape

from wagtail.models import Site

from taggit.models import Tag

from folioblog.blog.factories import (
    BlogCategoryFactory, BlogIndexPageFactory, BlogPageFactory, BlogTagFactory,
)
from folioblog.blog.models import BlogCategory, BlogPage
from folioblog.core.models import FolioBlogSettings
from folioblog.core.templatetags.folioblog import mimetype
from folioblog.search.factories import SearchIndexPageFactory
from folioblog.search.tests.units.htmlpages import SearchIndexHTMLPage


class SearchIndexPageTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.site = Site.objects.get(is_default_site=True)

        super().setUpClass()

        cls.folio_settings = FolioBlogSettings.load()
        cls.folio_settings.search_limit = 3
        cls.folio_settings.save()

    @classmethod
    def setUpTestData(cls):
        cls.index = BlogIndexPageFactory(parent=cls.site.root_page)
        cls.page = SearchIndexPageFactory(parent=cls.site.root_page)

    def tearDown(self):
        BlogPage.objects.all().delete()
        BlogCategory.objects.all().delete()
        Tag.objects.all().delete()

    @override_settings(LANGUAGE_CODE='fr-fr')
    def test_page_initial(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_filters'])
        self.assertFalse(response.context['search_results'])
        self.assertNotContains(response, escape('résultat'))

    def test_options_tags(self):
        p = BlogPageFactory(parent=self.index, tags__number=2)

        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_filters'])
        self.assertListEqual(
            sorted(response.context['tag_options']),
            sorted([t.slug for t in p.tags.all()]),
        )

    def test_options_categories(self):
        c1 = BlogCategoryFactory(name='tech')
        c2 = BlogCategoryFactory(name='economie')

        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_filters'])
        self.assertListEqual(
            sorted([c.pk for c in response.context['category_options']]),
            sorted([c.pk for c in [c1, c2]]),
        )

    @override_settings(LANGUAGE_CODE='fr-fr')
    def test_result_none(self):
        BlogPageFactory(parent=self.index, title='foo', subheading='', intro='', body='')
        BlogPageFactory(parent=self.index, title='bar', subheading='', intro='', body='')

        response = self.client.get(self.page.url, data={
            'query': 'miraculous',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['has_filters'])
        self.assertFalse(response.context['search_results'])
        self.assertContains(response, escape('0 résultat'), count=1)

    def test_invalid_tag(self):
        BlogTagFactory(name='foo')
        BlogTagFactory(name='bar')

        response = self.client.get(self.page.url, data={
            'tags': 'joe,dalton',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_filters'])
        self.assertTrue(response.context['form'].errors['tags'])

    def test_invalid_category(self):
        BlogCategoryFactory(name='foo')
        BlogCategoryFactory(name='bar')

        response = self.client.get(self.page.url, data={
            'categories': 'joe,dalton',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_filters'])
        self.assertTrue(response.context['form'].errors['categories'])

    @override_settings(LANGUAGE_CODE='fr-fr')
    def test_invalid_page_not_integer(self):
        p1 = BlogPageFactory(parent=self.index, title='foo', subheading='', intro='', body='')
        p2 = BlogPageFactory(parent=self.index, title='foo bar', subheading='', intro='', body='')

        response = self.client.get(self.page.url, data={
            'query': 'foo',
            'page': 'foo',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['has_filters'])
        self.assertEqual(len(response.context['search_results']), 2)
        self.assertListEqual(
            sorted([p.pk for p in response.context['search_results']]),
            sorted([p.pk for p in [p1, p2]])
        )
        self.assertEqual(response.context['search_results'].number, 1)

    @override_settings(LANGUAGE_CODE='fr-fr')
    def test_invalid_page_search(self):
        BlogPageFactory(parent=self.index, title='foo', subheading='', intro='', body='')
        BlogPageFactory(parent=self.index, title='bar', subheading='', intro='', body='')

        response = self.client.get(self.page.url, data={
            'query': 'foo',
            'page': 50,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['search_results'])
        self.assertNotContains(response, escape('résultat'))

    @override_settings(LANGUAGE_CODE='fr-fr')
    def test_invalid_page_filter(self):
        cat = BlogCategoryFactory(name='tech')
        BlogPageFactory(parent=self.index, category=cat, title='foo', subheading='', intro='', body='')
        BlogPageFactory(parent=self.index, category=cat, title='bar', subheading='', intro='', body='')

        response = self.client.get(self.page.url, data={
            'categories': [cat.slug],
            'page': 50,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['search_results'])
        self.assertNotContains(response, escape('résultat'))

    def test_live_not(self):
        p1 = BlogPageFactory(parent=self.index, live=True, title='foo', subheading='querymatch', intro='', body='')
        BlogPageFactory(parent=self.index, live=False, title='bar', subheading='querymatch', intro='', body='')

        response = self.client.get(self.page.url, data={
            'query': 'querymatch',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['search_results']), 1)
        self.assertEqual(response.context['search_results'][0].pk, p1.pk)

    @override_settings(LANGUAGE_CODE='fr-fr')
    def test_filter_query(self):
        p1 = BlogPageFactory(parent=self.index, title='foo', subheading='', intro='', body='')
        BlogPageFactory(parent=self.index, title='bar', subheading='', intro='', body='')

        response = self.client.get(self.page.url, data={
            'query': 'foo',
        })
        html = unescape(response.content.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['search_results']), 1)
        self.assertEqual(response.context['search_results'][0].pk, p1.pk)
        self.assertIn('1 résultat', html)

    @override_settings(LANGUAGE_CODE='fr-fr')
    def test_filter_query_multiple(self):
        p1 = BlogPageFactory(parent=self.index, title='green lantern 1', subheading='', intro='', body='')
        p2 = BlogPageFactory(parent=self.index, title='green lantern 2', subheading='', intro='', body='')
        BlogPageFactory(parent=self.index, title='superman', subheading='', intro='', body='')

        response = self.client.get(self.page.url, data={
            'query': 'green lantern',
        })
        html = unescape(response.content.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['search_results']), 2)
        self.assertListEqual(
            sorted([p.pk for p in response.context['search_results']]),
            sorted([p1.pk, p2.pk]),
        )
        self.assertIn('2 résultats', html)

    def test_filter_category(self):
        c1 = BlogCategoryFactory(name='tech')
        c2 = BlogCategoryFactory(name='economie')

        p1 = BlogPageFactory(parent=self.index, category=c1)
        BlogPageFactory(parent=self.index, category=c2)

        response = self.client.get(self.page.url, data={
            'categories': [c1.slug],
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['search_results']), 1)
        self.assertEqual(response.context['search_results'][0].pk, p1.pk)

    def test_filter_categories(self):
        c1 = BlogCategoryFactory(name='tech')
        c2 = BlogCategoryFactory(name='economie')
        c3 = BlogCategoryFactory(name='philosophie')

        p1 = BlogPageFactory(parent=self.index, category=c1)
        p2 = BlogPageFactory(parent=self.index, category=c2)
        BlogPageFactory(parent=self.index, category=c3)

        response = self.client.get(self.page.url, data={
            'categories': [c1.slug, c2.slug],
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['search_results']), 2)
        self.assertListEqual(
            sorted([p.pk for p in response.context['search_results']]),
            sorted([p1.pk, p2.pk]),
        )

    def test_filter_tag(self):
        t1 = BlogTagFactory(name='foo')
        t2 = BlogTagFactory(name='bar')

        p1 = BlogPageFactory(parent=self.index, tags=[t1])
        BlogPageFactory(parent=self.index, tags=[t2])

        response = self.client.get(self.page.url, data={
            'tags': t1.slug,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['search_results']), 1)
        self.assertEqual(response.context['search_results'][0].pk, p1.pk)

    def test_filter_tags(self):
        t1 = BlogTagFactory(name='foo')
        t2 = BlogTagFactory(name='bar')
        t3 = BlogTagFactory(name='baz')

        p1 = BlogPageFactory(parent=self.index, tags=[t1, t3])
        p2 = BlogPageFactory(parent=self.index, tags=[t2])
        BlogPageFactory(parent=self.index, tags=[t3])

        response = self.client.get(self.page.url, data={
            'tags': f'{t1.slug},{t2.slug}',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['search_results']), 2)
        self.assertListEqual(
            sorted([p.pk for p in response.context['search_results']]),
            sorted([p1.pk, p2.pk]),
        )

    def test_pagination_search(self):
        limit = self.folio_settings.search_limit
        exceed = (limit * 2) + 1

        posts = {}
        for i in range(0, exceed):
            post = BlogPageFactory(parent=self.index, title=f'hallelujah test {i}')
            posts[post.pk] = post

        page = 2
        response = self.client.get(self.page.url, data={
            'query': 'hallelujah',
            'page': page,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['search_results']), limit)
        self.assertEqual(response.context['search_results'].number, page)
        self.assertEqual(response.context['search_results'].paginator.count, len(posts))
        self.assertEqual(response.context['search_results'].paginator.per_page, limit)
        self.assertEqual(response.context['search_results'].paginator.num_pages, 3)
        self.assertIn(response.context['search_results'][0].pk, posts)
        self.assertIn(response.context['search_results'][1].pk, posts)

    def test_pagination_filter(self):
        category = BlogCategoryFactory(name='tech')

        limit = self.folio_settings.search_limit
        exceed = (limit * 2) + 1

        posts = {}
        for i in range(0, exceed):
            post = BlogPageFactory(parent=self.index, category=category)
            posts[post.pk] = post

        page = 2
        response = self.client.get(self.page.url, data={
            'categories': [category.slug],
            'page': page,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['search_results']), limit)
        self.assertEqual(response.context['search_results'].paginator.count, len(posts))
        self.assertEqual(response.context['search_results'].paginator.per_page, limit)
        self.assertEqual(response.context['search_results'].paginator.num_pages, 3)
        self.assertIn(response.context['search_results'][0].pk, posts)
        self.assertIn(response.context['search_results'][1].pk, posts)


class SearchIndexHTMLTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.page = SearchIndexPageFactory()

    def setUp(self):
        response = self.client.get(self.page.url)
        self.htmlpage = SearchIndexHTMLPage(response)

    def test_title(self):
        self.assertEqual(self.htmlpage.get_title(), self.page.title)

    def test_masthead_content(self):
        masthead_txt = self.htmlpage.get_masterhead_content().replace('\n', '')
        self.assertIn(self.page.title, masthead_txt)
        self.assertIn(self.page.subheading, masthead_txt)

    def test_meta_og(self):
        meta = self.htmlpage.get_meta_og()
        rendition = self.page.image.get_rendition('fill-2400x1260|format-jpeg')
        self.assertEqual(meta['og:type'], 'website')
        self.assertEqual(meta['og:site_name'], self.page.get_site().site_name)
        self.assertEqual(meta['og:locale'], self.page.locale.language_code)
        self.assertEqual(meta['og:title'], self.page.title)
        self.assertEqual(meta['og:url'], self.page.full_url)
        self.assertEqual(meta['og:description'], self.page.seo_description)
        self.assertEqual(meta['og:image'], rendition.full_url)
        self.assertEqual(meta['og:image:type'], mimetype(rendition.url))
        self.assertEqual(int(meta['og:image:width']), rendition.width)
        self.assertEqual(int(meta['og:image:height']), rendition.height)
        self.assertEqual(meta['og:image:alt'], self.page.caption)

    def test_meta_twitter(self):
        meta = self.htmlpage.get_meta_twitter()
        self.assertEqual(meta['twitter:card'], 'summary')

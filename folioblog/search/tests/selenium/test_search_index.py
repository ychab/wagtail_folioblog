from django.test import override_settings

from folioblog.blog.factories import (
    BlogCategoryFactory, BlogIndexPageFactory, BlogPageFactory, BlogTagFactory,
)
from folioblog.core.models import FolioBlogSettings
from folioblog.core.utils.tests import (
    FolioBlogSeleniumServerTestCase, skip_mobile,
)
from folioblog.search.factories import SearchIndexPageFactory
from folioblog.search.tests.selenium.webpages import SearchIndexWebPage


class SearchIndexPageLiveTestCase(FolioBlogSeleniumServerTestCase):

    def setUp(self):
        super().setUp()

        self.foliosettings = FolioBlogSettings.load()
        self.foliosettings.search_limit = 2
        self.foliosettings.save()

        self.categories = [
            BlogCategoryFactory(name='tech'),
            BlogCategoryFactory(name='economie'),
            BlogCategoryFactory(name='philosophie'),
        ]
        self.tags = [
            BlogTagFactory(name='python'),
            BlogTagFactory(name='django'),
            BlogTagFactory(name='test'),
        ]

        self.index_posts = BlogIndexPageFactory(parent=self.site.root_page)
        self.posts = [
            BlogPageFactory(
                parent=self.index_posts,
                category=self.categories[0],
                tags=[self.tags[0], self.tags[1]],
                title='Tests are greats except scrolling',
            ),
            BlogPageFactory(
                parent=self.index_posts,
                category=self.categories[0],
                tags=[self.tags[1], self.tags[2]],
                title='Tests really sucks mostly scrolling',
            ),
            BlogPageFactory(
                parent=self.index_posts,
                category=self.categories[1],
                title='Never trusts users inputs, including scrolling',
            ),
        ]

        self.page = SearchIndexPageFactory(parent=self.site.root_page)

        self.webpage = SearchIndexWebPage(self.selenium)
        self.webpage.fetch_page(f'{self.live_server_url}{self.page.url}')
        self.webpage.cookies_accept()

    def test_masthead_image(self):
        spec = 'fill-1080x1380' if self.is_mobile else 'fill-1905x560'
        rendition = self.page.image.get_rendition(spec)
        rendition_url = f'{self.live_server_url}{rendition.url}'
        self.assertEqual(rendition_url, self.webpage.get_masterhead_image())

    @skip_mobile()
    def test_query_no_result(self):
        done = self.webpage.search('bmofhbdsqmovfsbvnnmn')
        self.assertTrue(done)

        items = self.webpage.get_search_results()
        self.assertEqual(len(items), 0)

    def test_query_match(self):
        done = self.webpage.search('test')
        self.assertTrue(done)

        items = self.webpage.get_search_results()
        self.assertEqual(len(items), 2)

    @override_settings(LANGUAGE_CODE='fr-fr')
    def test_result_item(self):
        done = self.webpage.search('great')
        self.assertTrue(done)

        items = self.webpage.get_search_results()
        self.assertEqual(len(items), 1)
        self.assertIn('1 résultat', self.webpage.get_content())
        item = items[0]

        post = self.posts[0]
        post_url = f'{self.live_server_url}{post.url}'
        spec = 'width-936' if self.is_mobile else 'width-700'
        rendition = post.image.get_rendition(spec)
        rendition_url = f'{self.live_server_url}{rendition.url}'

        self.assertEqual(item['href'], post_url)
        self.assertEqual(item['title'], post.title)
        self.assertEqual(item['subtitle'], post.subheading)
        self.assertEqual(item['intro'], post.intro)
        self.assertEqual(item['img_src'], rendition_url)
        self.assertEqual(item['tags'], ' '.join([t.name for t in post.tags.all()]))

    def test_query_autocomplete_select(self):
        self.webpage.scroll_to_form()

        query = 'great'
        post = self.posts[0]
        post_url = f'{self.live_server_url}{post.url}'

        item = self.webpage.autocomplete(query)[0]
        self.assertEqual(post.title, item['title'])
        self.assertEqual(post_url, item['href'])

        is_selected = self.webpage.autocomplete_select(item)
        self.assertTrue(is_selected)

        self.webpage.scroll_to_top()

    def test_query_autocomplete_goto(self):
        self.webpage.scroll_to_form()

        query = 'great'
        post = self.posts[0]
        post_url = f'{self.live_server_url}{post.url}'

        item = self.webpage.autocomplete(query)[0]
        self.assertEqual(post.title, item['title'])
        self.assertEqual(post_url, item['href'])

        new_title = self.webpage.autocomplete_goto(item)
        self.assertEqual(new_title, post.title)
        self.assertEqual(self.webpage.url, post_url)

        self.webpage.scroll_to_top()

    def test_tag_autocomplete(self):
        self.webpage.scroll_to_form()

        self.webpage.tag_autocomplete('pyth')
        items = self.webpage.get_tag_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['value'], self.tags[0].slug)

        is_selected = self.webpage.tag_autocomplete_select(items[0]['elem'])
        self.assertTrue(is_selected)

        self.webpage.scroll_to_top()

    def test_tag_autocomplete_keys(self):
        self.webpage.scroll_to_form()

        self.webpage.tag_autocomplete('pyth')
        items = self.webpage.get_tag_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['value'], self.tags[0].slug)

        is_selected = self.webpage.tag_autocomplete_select_keys(1, items[0]['value'])
        self.assertTrue(is_selected)

        self.webpage.scroll_to_top()

    def test_filter_tag(self):
        self.webpage.scroll_to_form()

        items = self.webpage.filter_tag(self.tags[0].slug)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['title'], self.posts[0].title)

        self.webpage.scroll_to_top()

    def test_filter_tags(self):
        self.webpage.scroll_to_form()

        items = self.webpage.filter_tag(self.tags[1].slug)
        self.assertEqual(len(items), 2)

        titles = [i['title'] for i in items]
        self.assertIn(self.posts[0].title, titles)
        self.assertIn(self.posts[1].title, titles)

        self.webpage.scroll_to_top()

    def test_scrolling(self):
        done = self.webpage.search('scrolling')
        self.assertTrue(done)

        items = self.webpage.get_search_results()
        self.assertEqual(len(items), 2)

        self.webpage.scroll_to_results(expected_count=3)
        items = self.webpage.get_search_results()
        self.assertEqual(len(items), 3)
        self.webpage.scroll_to_top()

    def test_filter_category(self):
        self.webpage.scroll_to_form()

        is_filtered = self.webpage.filter_category(self.categories[1].slug)
        self.assertTrue(is_filtered)

        items = self.webpage.get_search_results()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['title'], self.posts[2].title)

        self.webpage.scroll_to_top()

    def test_filter_categories(self):
        self.webpage.scroll_to_form()

        is_filtered = self.webpage.filter_category(self.categories[0].slug)
        self.assertTrue(is_filtered)

        items = self.webpage.get_search_results()
        self.assertEqual(len(items), 2)

        titles = [i['title'] for i in items]
        self.assertIn(self.posts[0].title, titles)
        self.assertIn(self.posts[1].title, titles)

        self.webpage.scroll_to_top()

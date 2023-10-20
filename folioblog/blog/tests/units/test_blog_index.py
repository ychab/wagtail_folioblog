from django.conf import settings
from django.test import TestCase

from folioblog.blog.factories import (
    BlogCategoryFactory,
    BlogIndexPageFactory,
    BlogPageFactory,
)
from folioblog.blog.models import BlogCategory, BlogPage
from folioblog.blog.tests.units.htmlpages import BlogIndexHTMLPage
from folioblog.core.factories import LocaleFactory
from folioblog.core.models import FolioBlogSettings
from folioblog.core.templatetags.folioblog import mimetype


class BlogIndexPageTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.folio_settings = FolioBlogSettings.load()
        cls.folio_settings.blog_pager_limit = 3
        cls.folio_settings.save()

    @classmethod
    def setUpTestData(cls):
        cls.page = BlogIndexPageFactory()

    def tearDown(self):
        BlogPage.objects.all().delete()
        BlogCategory.objects.all().delete()

    def tests_categories(self):
        BlogCategoryFactory(name="foo")
        BlogCategoryFactory(name="bar")
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["categories"]), 2)

    def test_list_none(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context["categories"]), 0)
        self.assertEqual(len(response.context["blogpages"]), 0)

    def test_list_live(self):
        BlogPageFactory(parent=self.page, live=False)
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["blogpages"]), 0)

    def test_list_pagination(self):
        limit = self.folio_settings.blog_pager_limit
        exceed = (limit * 2) + 1

        posts = []
        for i in range(0, exceed):
            posts.append(BlogPageFactory(parent=self.page, title=f"pager{i}"))
        posts.reverse()

        page = 2
        response = self.client.get(self.page.url, data={"page": page})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["blogpages"]), limit)
        self.assertEqual(response.context["blogpages"].number, page)
        self.assertEqual(response.context["blogpages"][0].pk, posts[3].pk)
        self.assertEqual(response.context["blogpages"][1].pk, posts[4].pk)

    def test_list_pagination_invalid(self):
        limit = self.folio_settings.blog_pager_limit
        exceed = (limit * 2) + 1

        for i in range(0, exceed):
            BlogPageFactory(parent=self.page, title=f"pager{i}")

        page = 50
        response = self.client.get(self.page.url, data={"page": page})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["blogpages"]), 0)

    def test_list_order(self):
        posts = []
        for i in range(0, 3):
            posts.append(BlogPageFactory(parent=self.page))
        posts.reverse()

        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["blogpages"]), 3)

        self.assertEqual(response.context["blogpages"][0].pk, posts[0].pk)
        self.assertEqual(response.context["blogpages"][1].pk, posts[1].pk)
        self.assertEqual(response.context["blogpages"][2].pk, posts[2].pk)

    def test_list_filter_category(self):
        p1 = BlogPageFactory(parent=self.page, category__name="tech")
        BlogPageFactory(parent=self.page, category__name="economie")

        response = self.client.get(self.page.url, data={"category": "tech"})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context["blogpages"]), 1)
        self.assertEqual(response.context["blogpages"][0].pk, p1.pk)


class BlogIndexI18nPageTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        locale_fr = LocaleFactory(language_code="fr")
        locale_en = LocaleFactory(language_code="en")

        cls.page_fr = BlogIndexPageFactory(
            locale=locale_fr,
        )
        cls.page_en = cls.page_fr.copy_for_translation(
            locale=locale_en,
            copy_parents=True,
            alias=True,
        )

        cls.categories_fr = [
            BlogCategoryFactory(locale=locale_fr, name="Humour"),
            BlogCategoryFactory(locale=locale_fr, name="Cinéma"),
            BlogCategoryFactory(locale=locale_fr, name="Tutoriel"),
        ]

        for i in range(0, 3):
            post_fr = BlogPageFactory(
                parent=cls.page_fr,
                category=cls.categories_fr[i],
                locale=locale_fr,
            )
            if i == 0:
                category_en = cls.categories_fr[i].copy_for_translation(locale_en)
                category_en.save()

                post_en = post_fr.copy_for_translation(
                    locale=locale_en,
                    copy_parents=True,
                    alias=True,
                )
                post_en.category = category_en
                post_en.save()

    def test_filter_language_fr(self):
        response = self.client.get(self.page_fr.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context["blogpages"]), 3)
        self.assertListEqual(
            list(set(v.locale.language_code for v in response.context["blogpages"])),
            ["fr"],
        )
        self.assertEqual(len(response.context["categories"]), 3)
        self.assertListEqual(
            list(set(c.locale.language_code for c in response.context["categories"])),
            ["fr"],
        )

    def test_filter_language_en(self):
        response = self.client.get(self.page_en.url)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.context["blogpages"]), 1)
        self.assertEqual(response.context["blogpages"][0].locale.language_code, "en")

        self.assertEqual(len(response.context["categories"]), 1)
        self.assertEqual(response.context["categories"][0].locale.language_code, "en")


class BlogIndexHTMLTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.page = BlogIndexPageFactory()
        cls.categories = [
            BlogCategoryFactory(name="Tech"),
            BlogCategoryFactory(name="Économie"),
            BlogCategoryFactory(name="Philosophie"),
        ]

    def setUp(self):
        response = self.client.get(self.page.url)
        self.htmlpage = BlogIndexHTMLPage(response)

    def test_title(self):
        self.assertEqual(self.htmlpage.get_title(), self.page.title)

    def test_masthead_content(self):
        masthead_txt = self.htmlpage.get_masterhead_content().replace("\n", "")
        self.assertIn(self.page.title, masthead_txt)
        self.assertIn(self.page.subheading, masthead_txt)

    def test_meta_og(self):
        meta = self.htmlpage.get_meta_og()
        rendition = self.page.image.get_rendition("fill-2400x1260|format-jpeg")
        self.assertEqual(meta["og:type"], "website")
        self.assertEqual(meta["og:site_name"], self.page.get_site().site_name)
        self.assertEqual(meta["og:locale"], self.page.locale.language_code)
        self.assertEqual(meta["og:title"], self.page.title)
        self.assertEqual(meta["og:url"], self.page.full_url)
        self.assertEqual(meta["og:description"], self.page.seo_description)
        self.assertEqual(meta["og:image"], rendition.full_url)
        self.assertEqual(meta["og:image:type"], mimetype(rendition.url))
        self.assertEqual(int(meta["og:image:width"]), rendition.width)
        self.assertEqual(int(meta["og:image:height"]), rendition.height)
        self.assertEqual(meta["og:image:alt"], self.page.caption)

    def test_meta_twitter(self):
        meta = self.htmlpage.get_meta_twitter()
        self.assertEqual(meta["twitter:card"], "summary")

    def test_meta_canonical(self):
        href = self.htmlpage.get_canonical_href()
        self.assertEqual(href, self.page.full_url)

    def test_categories(self):
        filters = self.htmlpage.get_filter_categories()
        self.assertEqual(len(filters), len(self.categories))

        slugs = filters.keys()
        self.assertIn(self.categories[0].slug, slugs)
        self.assertIn(self.categories[1].slug, slugs)
        self.assertIn(self.categories[2].slug, slugs)


class BlogIndexHTMLi18nTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.page_fr = BlogIndexPageFactory(
            locale=LocaleFactory(language_code="fr"),
        )
        cls.page_en = cls.page_fr.copy_for_translation(
            locale=LocaleFactory(language_code="en"),
            copy_parents=True,
            alias=True,
        )

    def test_lang_default(self):
        response = self.client.get(self.page_fr.url)
        htmlpage = BlogIndexHTMLPage(response)
        self.assertEqual(htmlpage.get_meta_lang(), settings.LANGUAGE_CODE)

    def test_lang_fr(self):
        response = self.client.get(self.page_fr.url)
        htmlpage = BlogIndexHTMLPage(response)
        self.assertEqual(htmlpage.get_meta_lang(), self.page_fr.locale.language_code)

    def test_lang_en(self):
        response = self.client.get(self.page_en.url)
        htmlpage = BlogIndexHTMLPage(response)
        self.assertEqual(htmlpage.get_meta_lang(), self.page_en.locale.language_code)

    def test_alternates(self):
        response = self.client.get(self.page_fr.url)
        htmlpage = BlogIndexHTMLPage(response)

        self.assertListEqual(
            sorted(htmlpage.get_meta_alternates()),
            sorted([page.full_url for page in [self.page_fr, self.page_en]]),
        )

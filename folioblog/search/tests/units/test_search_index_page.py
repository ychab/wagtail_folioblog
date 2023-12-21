from html import unescape

from django.conf import settings
from django.test import TestCase
from django.utils import translation
from django.utils.html import escape

from wagtail.models import Site

from taggit.models import Tag
from wagtail_factories import SiteFactory

from folioblog.blog.factories import (
    BlogCategoryFactory,
    BlogIndexPageFactory,
    BlogPageFactory,
    BlogTagFactory,
)
from folioblog.blog.models import BlogCategory, BlogPage
from folioblog.core.factories import LocaleFactory
from folioblog.core.models import FolioBlogSettings
from folioblog.core.templatetags.folioblog import mimetype
from folioblog.home.factories import HomePageFactory
from folioblog.search.factories import SearchIndexPageFactory
from folioblog.search.tests.units.htmlpages import SearchIndexHTMLPage


class SearchIndexPageTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)

        cls.folio_settings = FolioBlogSettings.for_site(cls.site)
        cls.folio_settings.search_limit = 3
        cls.folio_settings.save()

        cls.index = BlogIndexPageFactory(parent=cls.site.root_page)
        cls.page = SearchIndexPageFactory(parent=cls.site.root_page)

    def tearDown(self):
        BlogPage.objects.all().delete()
        BlogCategory.objects.all().delete()
        Tag.objects.all().delete()

        translation.activate(settings.LANGUAGE_CODE)

    def test_page_initial(self):
        response = self.client.get(self.page.url, headers={"accept-language": "fr"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["has_filters"])
        self.assertFalse(response.context["search_results"])
        self.assertNotContains(response, escape("résultat"))

    def test_options_tags(self):
        p = BlogPageFactory(parent=self.index, tags__number=2)

        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["has_filters"])
        self.assertListEqual(
            sorted(response.context["tag_options"]),
            sorted([t.slug for t in p.tags.all()]),
        )

    def test_options_categories(self):
        c1 = BlogCategoryFactory(name="tech")
        c2 = BlogCategoryFactory(name="economie")

        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["has_filters"])
        self.assertListEqual(
            sorted([c.pk for c in response.context["category_options"]]),
            sorted([c.pk for c in [c1, c2]]),
        )

    def test_result_none(self):
        BlogPageFactory(
            parent=self.index, title="foo", subheading="", intro="", body=""
        )
        BlogPageFactory(
            parent=self.index, title="bar", subheading="", intro="", body=""
        )

        response = self.client.get(
            self.page.url,
            data={
                "query": "miraculous",
            },
            headers={"accept-language": "fr"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["has_filters"])
        self.assertFalse(response.context["search_results"])
        self.assertContains(response, escape("0 résultat"), count=1)

    def test_invalid_tag(self):
        BlogTagFactory(name="foo")
        BlogTagFactory(name="bar")

        response = self.client.get(
            self.page.url,
            data={
                "tags": "joe,dalton",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["has_filters"])
        self.assertTrue(response.context["form"].errors["tags"])

    def test_invalid_category(self):
        BlogCategoryFactory(name="foo")
        BlogCategoryFactory(name="bar")

        response = self.client.get(
            self.page.url,
            data={
                "categories": "joe,dalton",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["has_filters"])
        self.assertTrue(response.context["form"].errors["categories"])

    def test_invalid_page_not_integer(self):
        p1 = BlogPageFactory(
            parent=self.index, title="foo", subheading="", intro="", body=""
        )
        p2 = BlogPageFactory(
            parent=self.index, title="foo bar", subheading="", intro="", body=""
        )

        response = self.client.get(
            self.page.url,
            data={
                "query": "foo",
                "page": "foo",
            },
            headers={"accept-language": "fr"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["has_filters"])
        self.assertEqual(len(response.context["search_results"]), 2)
        self.assertListEqual(
            sorted([p.pk for p in response.context["search_results"]]),
            sorted([p.pk for p in [p1, p2]]),
        )
        self.assertEqual(response.context["search_results"].number, 1)

    def test_invalid_page_search(self):
        BlogPageFactory(
            parent=self.index, title="foo", subheading="", intro="", body=""
        )
        BlogPageFactory(
            parent=self.index, title="bar", subheading="", intro="", body=""
        )

        response = self.client.get(
            self.page.url,
            data={
                "query": "foo",
                "page": 50,
            },
            headers={"accept-language": "fr"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["search_results"])
        self.assertContains(response, escape("Aucun résultat"))

    def test_invalid_page_filter(self):
        cat = BlogCategoryFactory(name="tech")
        BlogPageFactory(
            parent=self.index,
            category=cat,
            title="foo",
            subheading="",
            intro="",
            body="",
        )
        BlogPageFactory(
            parent=self.index,
            category=cat,
            title="bar",
            subheading="",
            intro="",
            body="",
        )

        response = self.client.get(
            self.page.url,
            data={
                "categories": [cat.slug],
                "page": 50,
            },
            headers={"accept-language": "fr"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["search_results"])
        self.assertContains(response, escape("Aucun résultat"))

    def test_live_not(self):
        p1 = BlogPageFactory(
            parent=self.index,
            live=True,
            title="foo",
            subheading="querymatch",
            intro="",
            body="",
        )
        BlogPageFactory(
            parent=self.index,
            live=False,
            title="bar",
            subheading="querymatch",
            intro="",
            body="",
        )

        response = self.client.get(
            self.page.url,
            data={
                "query": "querymatch",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["search_results"]), 1)
        self.assertEqual(response.context["search_results"][0].pk, p1.pk)

    def test_filter_query(self):
        p1 = BlogPageFactory(
            parent=self.index, title="foo", subheading="", intro="", body=""
        )
        BlogPageFactory(
            parent=self.index, title="bar", subheading="", intro="", body=""
        )

        response = self.client.get(
            self.page.url,
            data={
                "query": "foo",
            },
            headers={"accept-language": "fr"},
        )
        html = unescape(response.content.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["search_results"]), 1)
        self.assertEqual(response.context["search_results"][0].pk, p1.pk)
        self.assertIn("1 résultat", html)

    def test_filter_query_multiple(self):
        p1 = BlogPageFactory(
            parent=self.index, title="green lantern 1", subheading="", intro="", body=""
        )
        p2 = BlogPageFactory(
            parent=self.index, title="green lantern 2", subheading="", intro="", body=""
        )
        BlogPageFactory(
            parent=self.index, title="superman", subheading="", intro="", body=""
        )

        response = self.client.get(
            self.page.url,
            data={
                "query": "green lantern",
            },
            headers={"accept-language": "fr"},
        )
        html = unescape(response.content.decode())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["search_results"]), 2)
        self.assertListEqual(
            sorted([p.pk for p in response.context["search_results"]]),
            sorted([p1.pk, p2.pk]),
        )
        self.assertIn("2 résultats", html)

    def test_filter_category(self):
        c1 = BlogCategoryFactory(name="tech")
        c2 = BlogCategoryFactory(name="economie")

        p1 = BlogPageFactory(parent=self.index, category=c1)
        BlogPageFactory(parent=self.index, category=c2)

        response = self.client.get(
            self.page.url,
            data={
                "categories": [c1.slug],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["search_results"]), 1)
        self.assertEqual(response.context["search_results"][0].pk, p1.pk)

    def test_filter_categories(self):
        c1 = BlogCategoryFactory(name="tech")
        c2 = BlogCategoryFactory(name="economie")
        c3 = BlogCategoryFactory(name="philosophie")

        p1 = BlogPageFactory(parent=self.index, category=c1)
        p2 = BlogPageFactory(parent=self.index, category=c2)
        BlogPageFactory(parent=self.index, category=c3)

        response = self.client.get(
            self.page.url,
            data={
                "categories": [c1.slug, c2.slug],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["search_results"]), 2)
        self.assertListEqual(
            sorted([p.pk for p in response.context["search_results"]]),
            sorted([p1.pk, p2.pk]),
        )

    def test_filter_tag(self):
        t1 = BlogTagFactory(name="foo")
        t2 = BlogTagFactory(name="bar")

        p1 = BlogPageFactory(parent=self.index, tags=[t1])
        BlogPageFactory(parent=self.index, tags=[t2])

        response = self.client.get(
            self.page.url,
            data={
                "tags": t1.slug,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["search_results"]), 1)
        self.assertEqual(response.context["search_results"][0].pk, p1.pk)

    def test_filter_tags(self):
        t1 = BlogTagFactory(name="foo")
        t2 = BlogTagFactory(name="bar")
        t3 = BlogTagFactory(name="baz")

        p1 = BlogPageFactory(parent=self.index, tags=[t1, t3])
        p2 = BlogPageFactory(parent=self.index, tags=[t2])
        BlogPageFactory(parent=self.index, tags=[t3])

        response = self.client.get(
            self.page.url,
            data={
                "tags": f"{t1.slug},{t2.slug}",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["search_results"]), 2)
        self.assertListEqual(
            sorted([p.pk for p in response.context["search_results"]]),
            sorted([p1.pk, p2.pk]),
        )

    def test_pagination_search(self):
        limit = self.folio_settings.search_limit
        exceed = (limit * 2) + 1

        posts = {}
        for i in range(0, exceed):
            post = BlogPageFactory(parent=self.index, title=f"hallelujah test {i}")
            posts[post.pk] = post

        page = 2
        response = self.client.get(
            self.page.url,
            data={
                "query": "hallelujah",
                "page": page,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["search_results"]), limit)
        self.assertEqual(response.context["search_results"].number, page)
        self.assertEqual(response.context["search_results"].paginator.count, len(posts))
        self.assertEqual(response.context["search_results"].paginator.per_page, limit)
        self.assertEqual(response.context["search_results"].paginator.num_pages, 3)
        self.assertIn(response.context["search_results"][0].pk, posts)
        self.assertIn(response.context["search_results"][1].pk, posts)

    def test_pagination_filter(self):
        category = BlogCategoryFactory(name="tech")

        limit = self.folio_settings.search_limit
        exceed = (limit * 2) + 1

        posts = {}
        for i in range(0, exceed):
            post = BlogPageFactory(parent=self.index, category=category)
            posts[post.pk] = post

        page = 2
        response = self.client.get(
            self.page.url,
            data={
                "categories": [category.slug],
                "page": page,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["search_results"]), limit)
        self.assertEqual(response.context["search_results"].paginator.count, len(posts))
        self.assertEqual(response.context["search_results"].paginator.per_page, limit)
        self.assertEqual(response.context["search_results"].paginator.num_pages, 3)
        self.assertIn(response.context["search_results"][0].pk, posts)
        self.assertIn(response.context["search_results"][1].pk, posts)


class SearchIndexI18nPageTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        locale_fr = LocaleFactory(language_code="fr")
        locale_en = LocaleFactory(language_code="en")

        site = Site.objects.get(is_default_site=True)
        cls.index_fr = BlogIndexPageFactory(
            parent=site.root_page,
            locale=locale_fr,
        )

        cls.categories_fr = [
            BlogCategoryFactory(locale=locale_fr, name="Humour"),
            BlogCategoryFactory(locale=locale_fr, name="Cinéma"),
            BlogCategoryFactory(locale=locale_fr, name="Tutoriel"),
        ]
        for i in range(0, 3):
            post_fr = BlogPageFactory(
                parent=cls.index_fr,
                category=cls.categories_fr[i],
                locale=locale_fr,
                title="titre",
                slug=f"titre_{i}",
            )
            if i == 0:
                category_en = cls.categories_fr[i].copy_for_translation(locale_en)
                category_en.name = "Comedy"
                category_en.save()

                post_en = post_fr.copy_for_translation(
                    locale=locale_en,
                    copy_parents=True,
                    alias=True,
                )
                post_en.title = "title"
                post_en.slug = "title_0"
                post_en.category = category_en
                post_en.save()

        cls.page_fr = SearchIndexPageFactory(
            parent=site.root_page,
            locale=locale_fr,
        )
        cls.page_en = cls.page_fr.copy_for_translation(
            locale=locale_en,
            copy_parents=True,
            alias=True,
        )

    def test_filter_language_fr(self):
        url = self.page_fr.url

        response = self.client.get(url, data={"query": "titre"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("/fr/", response.context["autocomplete_url"])
        self.assertNotIn("/en/", response.context["autocomplete_url"])

        self.assertEqual(response.context["search_counter"], 3)
        self.assertListEqual(
            list(
                set(p.locale.language_code for p in response.context["search_results"])
            ),
            ["fr"],
        )
        self.assertEqual(len(response.context["category_options"]), 3)
        self.assertListEqual(
            list(
                set(
                    c.locale.language_code for c in response.context["category_options"]
                )
            ),
            ["fr"],
        )

    def test_filter_language_en(self):
        url = self.page_en.url

        response = self.client.get(url, data={"query": "title"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("/en/", response.context["autocomplete_url"])

        self.assertEqual(response.context["search_counter"], 1)
        self.assertEqual(
            response.context["search_results"][0].locale.language_code, "en"
        )

        self.assertEqual(len(response.context["category_options"]), 1)
        self.assertEqual(
            response.context["category_options"][0].locale.language_code, "en"
        )


class SearchIndexMultiDomainTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)
        cls.home = HomePageFactory(parent=cls.site.root_page)
        cls.search = SearchIndexPageFactory(parent=cls.home)
        cls.index = BlogIndexPageFactory(parent=cls.home)
        cls.blog_cat = BlogCategoryFactory(slug="foo", site=cls.site)
        cls.blog_tag = BlogTagFactory(slug="foo", site=cls.site)
        cls.blog = BlogPageFactory(
            parent=cls.index,
            title="foobarbaz",
            category=cls.blog_cat,
            tags=[cls.blog_tag],
        )

        cls.home_other = HomePageFactory(parent=None)
        cls.site_other = SiteFactory(root_page=cls.home_other)
        cls.search_other = SearchIndexPageFactory(parent=cls.home_other)
        cls.index_other = BlogIndexPageFactory(parent=cls.home_other)
        cls.blog_cat_other = BlogCategoryFactory(slug="bar", site=cls.site_other)
        cls.blog_tag_other = BlogTagFactory(slug="bar", site=cls.site_other)
        cls.blog_other = BlogPageFactory(
            parent=cls.index_other,
            title="foobarbaz",
            category=cls.blog_cat_other,
            tags=[cls.blog_tag_other],
        )

    def test_filter_site(self):
        response = self.client.get(
            self.search.url,
            data={
                "query": "foobarbaz",
            },
        )
        self.assertEqual(response.status_code, 200)

        self.assertIn(self.blog.pk, [p.pk for p in response.context["search_results"]])
        self.assertNotIn(
            self.blog_other.pk, [p.pk for p in response.context["search_results"]]
        )

    def test_filter_categories(self):
        response = self.client.get(
            self.search.url,
            data={
                "categories": [self.blog_cat.slug],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context.get("errors"))
        self.assertEqual(len(response.context["category_options"]), 1)
        self.assertEqual(
            self.blog_cat.pk, response.context["category_options"].first().pk
        )

    def test_filter_categories_errors(self):
        response = self.client.get(
            self.search.url,
            data={
                "categories": [self.blog_cat_other.slug],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["errors"]["categories"])

    def test_filter_tags(self):
        response = self.client.get(
            self.search.url,
            data={
                "tags": [self.blog_tag.slug],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context.get("errors"))
        self.assertEqual(len(response.context["tag_options"]), 1)
        self.assertIn(self.blog_tag.slug, response.context["tag_options"])

    def test_filter_tags_errors(self):
        response = self.client.get(
            self.search.url,
            data={
                "tags": [self.blog_tag_other.slug],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["errors"]["tags"])


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


class SearchIndexHTMLi18nTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.page_fr = SearchIndexPageFactory(
            locale=LocaleFactory(language_code="fr"),
        )
        cls.page_en = cls.page_fr.copy_for_translation(
            locale=LocaleFactory(language_code="en"),
            copy_parents=True,
            alias=True,
        )

    def test_lang_default(self):
        response = self.client.get(self.page_fr.url)
        htmlpage = SearchIndexHTMLPage(response)
        self.assertEqual(htmlpage.get_meta_lang(), settings.LANGUAGE_CODE)

    def test_lang_fr(self):
        response = self.client.get(self.page_fr.url)
        htmlpage = SearchIndexHTMLPage(response)
        self.assertEqual(htmlpage.get_meta_lang(), self.page_fr.locale.language_code)

    def test_lang_en(self):
        response = self.client.get(self.page_en.url)
        htmlpage = SearchIndexHTMLPage(response)
        self.assertEqual(htmlpage.get_meta_lang(), self.page_en.locale.language_code)

    def test_alternates(self):
        response = self.client.get(self.page_fr.url)
        htmlpage = SearchIndexHTMLPage(response)

        self.assertListEqual(
            sorted(htmlpage.get_meta_alternates()),
            sorted([page.full_url for page in [self.page_fr, self.page_en]]),
        )

from django.test import TestCase, override_settings
from django.urls import reverse

from wagtail.models import Site

from wagtail_factories import SiteFactory

from folioblog.blog.factories import BlogIndexPageFactory, BlogPageFactory
from folioblog.blog.models import BlogPage


class BlogPageListAPIViewSetTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)
        cls.index = BlogIndexPageFactory(parent=cls.site.root_page)

        cls.other_site = SiteFactory()
        cls.other_index = BlogIndexPageFactory(parent=cls.other_site.root_page)

        cls.url = reverse("folioblogapi:posts:listing")

    def tearDown(self):
        BlogPage.objects.all().delete()

    def test_list_param_site_excluded(self):
        response = self.client.get(
            self.url,
            data={
                "site": self.other_site.pk,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["message"],
            "query parameter is not an operation or a recognised field: site",
        )

    def test_list_param_type_excluded(self):
        response = self.client.get(
            self.url,
            data={
                "type": "BlogPage",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["message"],
            "query parameter is not an operation or a recognised field: type",
        )

    def test_list_exclude_not_published(self):
        post = BlogPageFactory(parent=self.index, live=True)
        BlogPageFactory(parent=self.index, live=False)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["meta"]["total_count"], 1)
        self.assertEqual(response.data["items"][0]["id"], post.pk)

    def test_list_exclude_private(self):
        post = BlogPageFactory(parent=self.index)
        BlogPageFactory(parent=self.index, is_private=True)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["meta"]["total_count"], 1)
        self.assertEqual(response.data["items"][0]["id"], post.pk)

    def test_list_exclude_other_site(self):
        post = BlogPageFactory(parent=self.index)
        BlogPageFactory(parent=self.other_index)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["meta"]["total_count"], 1)
        self.assertEqual(response.data["items"][0]["id"], post.pk)

    @override_settings(WAGTAILAPI_LIMIT_MAX=20)
    def test_list(self):
        total = 3
        for i in range(0, total):
            BlogPageFactory(parent=self.index)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["meta"]["total_count"], total)
        self.assertEqual(len(response.data["items"]), total)

    def test_list_extra_fields(self):
        post = BlogPageFactory(parent=self.index, tags__number=3)

        response = self.client.get(
            self.url,
            data={
                "fields": "*,category(*),image(*,photographer(*))",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["meta"]["total_count"], 1)

        self.assertEqual(
            response.data["items"][0]["meta"]["date"], post.date.isoformat()
        )
        self.assertEqual(response.data["items"][0]["meta"]["author"], post.author)

        self.assertEqual(response.data["items"][0]["title"], post.title)
        self.assertEqual(response.data["items"][0]["body"], post.body)
        self.assertEqual(response.data["items"][0]["subheading"], post.subheading)
        self.assertEqual(response.data["items"][0]["image_alt"], post.image_alt)
        self.assertEqual(response.data["items"][0]["intro"], post.intro)
        self.assertEqual(response.data["items"][0]["image_body"], post.image_body)
        self.assertEqual(response.data["items"][0]["blockquote"], post.blockquote)
        self.assertEqual(
            response.data["items"][0]["blockquote_author"], post.blockquote_author
        )
        self.assertEqual(
            response.data["items"][0]["blockquote_ref"], post.blockquote_ref
        )

        self.assertEqual(response.data["items"][0]["category"]["id"], post.category.pk)
        self.assertEqual(
            response.data["items"][0]["category"]["name"], post.category.name
        )
        self.assertEqual(
            response.data["items"][0]["category"]["slug"], post.category.slug
        )

        self.assertEqual(response.data["items"][0]["image"]["id"], post.image.pk)
        self.assertEqual(response.data["items"][0]["image"]["title"], post.image.title)
        self.assertEqual(response.data["items"][0]["image"]["width"], post.image.width)
        self.assertEqual(
            response.data["items"][0]["image"]["height"], post.image.height
        )
        self.assertEqual(
            response.data["items"][0]["image"]["caption"], post.image.caption
        )
        self.assertEqual(
            response.data["items"][0]["image"]["download_url"], post.image.file.url
        )
        self.assertEqual(
            response.data["items"][0]["image"]["photographer"]["id"],
            post.image.photographer.pk,
        )
        self.assertEqual(
            response.data["items"][0]["image"]["photographer"]["name"],
            post.image.photographer.name,
        )
        self.assertEqual(
            response.data["items"][0]["image"]["photographer"]["website"],
            post.image.photographer.website,
        )

        self.assertListEqual(
            sorted(response.data["items"][0]["tags"]),
            sorted([t.name for t in post.tags.all()]),
        )


class BlogPageDetailAPIViewSetTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)
        cls.index = BlogIndexPageFactory(parent=cls.site.root_page)

        cls.other_site = SiteFactory()
        cls.other_index = BlogIndexPageFactory(parent=cls.other_site.root_page)

    def test_detail_param_site(self):
        """If we don't override get_base_queryset(), invalid site throw an error in Wagtail!"""
        post = BlogPageFactory(parent=self.index)
        url = reverse("folioblogapi:posts:detail", kwargs={"pk": post.pk})

        response = self.client.get(url, data={"site": self.other_site.pk})
        self.assertEqual(response.status_code, 200)

    def test_detail_exclude_not_published(self):
        post = BlogPageFactory(parent=self.index, live=False)
        url = reverse("folioblogapi:posts:detail", kwargs={"pk": post.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data["message"], "No BlogPage matches the given query."
        )

    def test_detail_exclude_private(self):
        post = BlogPageFactory(parent=self.index, is_private=True)
        url = reverse("folioblogapi:posts:detail", kwargs={"pk": post.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data["message"], "No BlogPage matches the given query."
        )

    def test_detail_exclude_other_site(self):
        post = BlogPageFactory(parent=self.other_index)
        url = reverse("folioblogapi:posts:detail", kwargs={"pk": post.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data["message"], "No BlogPage matches the given query."
        )

    def test_detail_extra_fields(self):
        post = BlogPageFactory(parent=self.index, tags__number=3)
        url = reverse("folioblogapi:posts:detail", kwargs={"pk": post.pk})

        response = self.client.get(
            url,
            data={
                "fields": "*,category(*),image(*,photographer(*))",
            },
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data["meta"]["date"], post.date.isoformat())
        self.assertEqual(response.data["meta"]["author"], post.author)

        self.assertEqual(response.data["title"], post.title)
        self.assertEqual(response.data["body"], post.body)
        self.assertEqual(response.data["subheading"], post.subheading)
        self.assertEqual(response.data["image_alt"], post.image_alt)
        self.assertEqual(response.data["intro"], post.intro)
        self.assertEqual(response.data["image_body"], post.image_body)
        self.assertEqual(response.data["blockquote"], post.blockquote)
        self.assertEqual(response.data["blockquote_author"], post.blockquote_author)
        self.assertEqual(response.data["blockquote_ref"], post.blockquote_ref)

        self.assertEqual(response.data["category"]["id"], post.category.pk)
        self.assertEqual(response.data["category"]["name"], post.category.name)
        self.assertEqual(response.data["category"]["slug"], post.category.slug)

        self.assertEqual(response.data["image"]["id"], post.image.pk)
        self.assertEqual(response.data["image"]["title"], post.image.title)
        self.assertEqual(response.data["image"]["width"], post.image.width)
        self.assertEqual(response.data["image"]["height"], post.image.height)
        self.assertEqual(response.data["image"]["caption"], post.image.caption)
        self.assertEqual(response.data["image"]["download_url"], post.image.file.url)
        self.assertEqual(
            response.data["image"]["photographer"]["id"], post.image.photographer.pk
        )
        self.assertEqual(
            response.data["image"]["photographer"]["name"], post.image.photographer.name
        )
        self.assertEqual(
            response.data["image"]["photographer"]["website"],
            post.image.photographer.website,
        )

        self.assertListEqual(
            sorted(response.data["tags"]),
            sorted([t.name for t in post.tags.all()]),
        )

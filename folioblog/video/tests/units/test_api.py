from django.test import TestCase, override_settings
from django.urls import reverse

from wagtail.models import Site

from wagtail_factories import SiteFactory

from folioblog.video.factories import VideoIndexPageFactory, VideoPageFactory
from folioblog.video.models import VideoPage


class VideoPageListAPIViewSetTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)
        cls.index = VideoIndexPageFactory(parent=cls.site.root_page)

        cls.other_site = SiteFactory()
        cls.other_index = VideoIndexPageFactory(parent=cls.other_site.root_page)

        cls.url = reverse("folioblogapi:videos:listing")

    def tearDown(self):
        VideoPage.objects.all().delete()

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
                "type": "VideoPage",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["message"],
            "query parameter is not an operation or a recognised field: type",
        )

    def test_list_exclude_not_published(self):
        video = VideoPageFactory(parent=self.index, live=True)
        VideoPageFactory(parent=self.index, live=False)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["meta"]["total_count"], 1)
        self.assertEqual(response.data["items"][0]["id"], video.pk)

    def test_list_exclude_private(self):
        video = VideoPageFactory(parent=self.index)
        VideoPageFactory(parent=self.index, is_private=True)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["meta"]["total_count"], 1)
        self.assertEqual(response.data["items"][0]["id"], video.pk)

    def test_list_exclude_other_site(self):
        video = VideoPageFactory(parent=self.index)
        VideoPageFactory(parent=self.other_index)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["meta"]["total_count"], 1)
        self.assertEqual(response.data["items"][0]["id"], video.pk)

    @override_settings(WAGTAILAPI_LIMIT_MAX=20)
    def test_list(self):
        total = 3
        for i in range(0, total):
            VideoPageFactory(parent=self.index)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["meta"]["total_count"], total)
        self.assertEqual(len(response.data["items"]), total)

    def test_list_extra_fields(self):
        video = VideoPageFactory(parent=self.index, tags__number=3)

        response = self.client.get(
            self.url,
            data={
                "fields": "*,category(*),image(*,photographer(*))",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["meta"]["total_count"], 1)

        self.assertEqual(
            response.data["items"][0]["meta"]["date"], video.date.isoformat()
        )
        self.assertEqual(response.data["items"][0]["meta"]["author"], video.author)

        self.assertEqual(response.data["items"][0]["title"], video.title)
        self.assertEqual(response.data["items"][0]["body"], video.body)
        self.assertEqual(response.data["items"][0]["subheading"], video.subheading)
        self.assertEqual(response.data["items"][0]["image_alt"], video.image_alt)
        self.assertEqual(response.data["items"][0]["intro"], video.intro)
        self.assertEqual(response.data["items"][0]["video_url"], video.video_url)
        self.assertEqual(
            response.data["items"][0]["thumbnail"]["id"], video.thumbnail.pk
        )

        self.assertEqual(response.data["items"][0]["category"]["id"], video.category.pk)
        self.assertEqual(
            response.data["items"][0]["category"]["name"], video.category.name
        )
        self.assertEqual(
            response.data["items"][0]["category"]["slug"], video.category.slug
        )

        self.assertEqual(response.data["items"][0]["image"]["id"], video.image.pk)
        self.assertEqual(response.data["items"][0]["image"]["title"], video.image.title)
        self.assertEqual(response.data["items"][0]["image"]["width"], video.image.width)
        self.assertEqual(
            response.data["items"][0]["image"]["height"], video.image.height
        )
        self.assertEqual(
            response.data["items"][0]["image"]["caption"], video.image.caption
        )
        self.assertEqual(
            response.data["items"][0]["image"]["download_url"], video.image.file.url
        )
        self.assertEqual(
            response.data["items"][0]["image"]["photographer"]["id"],
            video.image.photographer.pk,
        )
        self.assertEqual(
            response.data["items"][0]["image"]["photographer"]["name"],
            video.image.photographer.name,
        )
        self.assertEqual(
            response.data["items"][0]["image"]["photographer"]["website"],
            video.image.photographer.website,
        )

        self.assertListEqual(
            sorted(response.data["items"][0]["tags"]),
            sorted([t.name for t in video.tags.all()]),
        )


class VideoPageDetailAPIViewSetTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)
        cls.index = VideoIndexPageFactory(parent=cls.site.root_page)

        cls.other_site = SiteFactory()
        cls.other_index = VideoIndexPageFactory(parent=cls.other_site.root_page)

    def test_detail_param_site(self):
        """If we don't override get_base_queryset(), invalid site throw an error in Wagtail!"""
        video = VideoPageFactory(parent=self.index)
        url = reverse("folioblogapi:videos:detail", kwargs={"pk": video.pk})

        response = self.client.get(url, data={"site": self.other_site.pk})
        self.assertEqual(response.status_code, 200)

    def test_detail_exclude_not_published(self):
        video = VideoPageFactory(parent=self.index, live=False)
        url = reverse("folioblogapi:videos:detail", kwargs={"pk": video.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data["message"], "No VideoPage matches the given query."
        )

    def test_detail_exclude_private(self):
        video = VideoPageFactory(parent=self.index, is_private=True)
        url = reverse("folioblogapi:videos:detail", kwargs={"pk": video.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data["message"], "No VideoPage matches the given query."
        )

    def test_detail_exclude_other_site(self):
        video = VideoPageFactory(parent=self.other_index)
        url = reverse("folioblogapi:videos:detail", kwargs={"pk": video.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data["message"], "No VideoPage matches the given query."
        )

    def test_detail_extra_fields(self):
        video = VideoPageFactory(parent=self.index, tags__number=3)
        url = reverse("folioblogapi:videos:detail", kwargs={"pk": video.pk})

        response = self.client.get(
            url,
            data={
                "fields": "*,category(*),image(*,photographer(*))",
            },
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data["meta"]["date"], video.date.isoformat())
        self.assertEqual(response.data["meta"]["author"], video.author)

        self.assertEqual(response.data["title"], video.title)
        self.assertEqual(response.data["body"], video.body)
        self.assertEqual(response.data["subheading"], video.subheading)
        self.assertEqual(response.data["image_alt"], video.image_alt)
        self.assertEqual(response.data["intro"], video.intro)
        self.assertEqual(response.data["video_url"], video.video_url)
        self.assertEqual(response.data["thumbnail"]["id"], video.thumbnail.pk)

        self.assertEqual(response.data["category"]["id"], video.category.pk)
        self.assertEqual(response.data["category"]["name"], video.category.name)
        self.assertEqual(response.data["category"]["slug"], video.category.slug)

        self.assertEqual(response.data["image"]["id"], video.image.pk)
        self.assertEqual(response.data["image"]["title"], video.image.title)
        self.assertEqual(response.data["image"]["width"], video.image.width)
        self.assertEqual(response.data["image"]["height"], video.image.height)
        self.assertEqual(response.data["image"]["caption"], video.image.caption)
        self.assertEqual(response.data["image"]["download_url"], video.image.file.url)
        self.assertEqual(
            response.data["image"]["photographer"]["id"], video.image.photographer.pk
        )
        self.assertEqual(
            response.data["image"]["photographer"]["name"],
            video.image.photographer.name,
        )
        self.assertEqual(
            response.data["image"]["photographer"]["website"],
            video.image.photographer.website,
        )

        self.assertListEqual(
            sorted(response.data["tags"]),
            sorted([t.name for t in video.tags.all()]),
        )

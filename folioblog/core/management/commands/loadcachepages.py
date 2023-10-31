import math

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import translation

from wagtail.models import Collection, Page, Site

import requests
from requests import RequestException

from folioblog.blog.models import BlogCategory, BlogPage
from folioblog.core.managers import qs_in_site_alt
from folioblog.core.models import FolioBlogSettings
from folioblog.video.models import VideoCategory, VideoPage


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.requests_kwargs = {}

    def add_arguments(self, parser):
        parser.add_argument("--auth-user")
        parser.add_argument("--auth-passwd")

    def handle(self, *args, **options):
        # Prepare request options
        if options["auth_user"] and options["auth_passwd"]:  # pragma: no cover
            self.requests_kwargs["auth"] = (
                options["auth_user"],
                options["auth_passwd"],
            )

        # Then clear the cache before rebuilding it!
        self.stdout.write(self.style.WARNING("WARNING: clearing cache...\n"))
        cache.clear()

        # Then iterate over each sites to fetch their pages.
        for site in Site.objects.all():
            self.process_site(site, FolioBlogSettings.for_site(site))

    def process_site(self, site, folio_settings):
        self.stdout.write(self.style.WARNING(f"About requesting pages of site {site}:"))

        # Fetch pages to build renditions and populate the cache!
        qs = Page.objects.live().order_by("pk")
        qs = qs_in_site_alt(qs, site)
        for page in qs:
            self.process_page(page, folio_settings)

        # Fetch views
        self.stdout.write(self.style.WARNING("About requesting views:"))
        views = ["javascript-catalog", "rss"]
        for lang in dict(settings.LANGUAGES).keys():
            for view_name in views:
                with translation.override(lang):
                    url = reverse(view_name)
                self.request_page(f"{site.root_url}{url}")

        # Don't forgot 404 page for renditions only (dummy url + not a 200 code)
        self.request_page(f"{site.root_url}/givemea404please", status=404)

        self.stdout.write(
            self.style.SUCCESS(f"All page cache loaded for site {site}.\n")
        )

    def process_page(self, page, folio_settings):
        # Request page without parameters.
        self.request_page(page.full_url)

        # Request pages with pagination only.
        limit = None
        if page.slug in ["posts", "videos"]:
            limit = (
                folio_settings.video_pager_limit
                if page.slug == "videos"
                else folio_settings.blog_pager_limit
            )
            self.request_pagination(page, limit)

        # Request pages with pagination AND filtering.
        if page.slug == "posts":
            self.request_filtering_blog_category(page, limit)
        if page.slug == "videos":
            self.request_filtering_video_category(page, limit)
        elif page.slug == "gallery":
            self.request_filtering_collection(page, folio_settings.gallery_collection)

    def request_page(self, full_url, status=None, **kwargs):
        self.stdout.write(f'Requesting: "{full_url}"')

        requests_kwargs = self.requests_kwargs | kwargs
        try:
            response = requests.get(full_url, **requests_kwargs)
        except RequestException as e:
            self.stdout.write(
                self.style.ERROR(f"Error on page {full_url} with exc {e}\n")
            )
        else:
            if (not status and not response.ok) or (
                status and status != response.status_code
            ):
                self.stdout.write(
                    self.style.WARNING(
                        f"Error for page {full_url} with status {response.status_code}.\n"
                    )
                )  # noqa

    def request_pagination(self, page, limit):
        total = Page.objects.descendant_of(page).live().count()
        num_pages = math.ceil(total / limit)
        for i in range(0, num_pages):
            self.request_page(
                f"{page.full_url}?ajax=1&page={i + 1}",
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                },
            )

    def request_filtering_collection(self, page, root_collection=None):
        qs_collection = Collection.objects.all()
        if root_collection:
            qs_collection = qs_collection.descendant_of(root_collection)

        for collection in qs_collection:
            self.request_page(
                f"{page.full_url}?ajax=1&collection={collection.pk}",
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                },
            )

    def request_filtering_blog_category(self, page, limit):
        categories = BlogCategory.objects.all()

        for category in categories:
            total = (
                BlogPage.objects.descendant_of(page)
                .live()
                .filter(category=category)
                .count()
            )
            num_pages = math.ceil(total / limit)

            for i in range(0, num_pages):
                self.request_page(
                    f"{page.full_url}?ajax=1&page={i + 1}&category={category.slug}",
                    headers={
                        "X-Requested-With": "XMLHttpRequest",
                    },
                )

    def request_filtering_video_category(self, page, limit):
        categories = VideoCategory.objects.all()

        for category in categories:
            total = (
                VideoPage.objects.descendant_of(page)
                .live()
                .filter(category=category)
                .count()
            )
            num_pages = math.ceil(total / limit)

            for i in range(0, num_pages):
                self.request_page(
                    f"{page.full_url}?ajax=1&page={i + 1}&category={category.slug}",
                    headers={
                        "X-Requested-With": "XMLHttpRequest",
                    },
                )

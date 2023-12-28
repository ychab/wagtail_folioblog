import math

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import translation

from wagtail.models import Collection, Page, Site

import requests
from requests import RequestException

from folioblog.blog.models import BlogCategory, BlogIndexPage, BlogPage
from folioblog.core.managers import qs_in_site_alt
from folioblog.core.models import FolioBlogSettings
from folioblog.gallery.models import GalleryPage
from folioblog.video.models import VideoCategory, VideoIndexPage, VideoPage


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = requests.session()

    def handle(self, *args, **options):
        # First clear the cache before rebuilding it!
        self.stdout.write(self.style.WARNING("WARNING: clearing cache...\n"))
        cache.clear()

        # Then iterate over each sites to fetch their pages.
        for site in Site.objects.all():
            self.process_site(site, FolioBlogSettings.for_site(site))

    def process_site(self, site, folio_settings):
        self.stdout.write(self.style.WARNING(f"About requesting pages of site {site}:"))

        # Fetch pages with translations to build renditions and page cache.
        qs = Page.objects.live().public().order_by("pk")
        qs = qs_in_site_alt(qs, site)
        for page in qs:
            self.process_page(page, folio_settings)

        # Fetch views
        self.stdout.write(self.style.WARNING("About requesting views:"))
        self.process_view(site)

        # Finally don't forgot 404 page for renditions ONLY (ie: not the url)
        self.request_page(f"{site.root_url}/givemea404please", status=404)

        self.stdout.write(
            self.style.SUCCESS(f"All page cache loaded for site {site}.\n")
        )

    def process_page(self, page, folio_settings):
        # First request page without parameters.
        self.request_page(page.full_url)

        # Then request pages with pagination.
        limit = None
        if page.specific_class in [BlogIndexPage, VideoIndexPage]:
            limit = (
                folio_settings.video_pager_limit
                if page.specific_class is VideoIndexPage
                else folio_settings.blog_pager_limit
            )
            self.request_pagination(page, limit)

        # Then request pages with pagination AND filtering.
        if page.specific_class is BlogIndexPage:
            self.request_filtering_blog_category(folio_settings.site, page, limit)
        elif page.specific_class is VideoIndexPage:
            self.request_filtering_video_category(folio_settings.site, page, limit)
        elif page.specific_class is GalleryPage:
            self.request_filtering_collection(page, folio_settings.gallery_collection)

    def process_view(self, site):
        views = ["javascript-catalog", "rss"]
        for lang in dict(settings.LANGUAGES).keys():
            for view_name in views:
                with translation.override(lang):
                    url = reverse(view_name)
                self.request_page(f"{site.root_url}{url}")

    def request_page(self, url, method="get", status=None, **kwargs):
        self.stdout.write(f'Requesting: {method.upper()} "{url}"')

        try:
            response = getattr(self.session, method)(url, **kwargs)
        except RequestException as e:
            self.stdout.write(self.style.ERROR(f"Error on page {url} with exc {e}\n"))
        else:
            if (not status and not response.ok) or (
                status and status != response.status_code
            ):
                self.stdout.write(
                    self.style.WARNING(
                        f"Error for page {url} with status {response.status_code}.\n"
                    )
                )
            return response

    def request_pagination(self, page, limit):
        total = Page.objects.descendant_of(page).live().count()
        num_pages = math.ceil(total / limit)
        for i in range(0, num_pages):
            self.request_page(
                url=f"{page.full_url}?ajax=1&page={i + 1}",
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
                url=f"{page.full_url}?ajax=1&collection={collection.pk}",
                headers={
                    "X-Requested-With": "XMLHttpRequest",
                },
            )

    def request_filtering_blog_category(self, site, page, limit):
        categories = BlogCategory.objects.in_site(site)

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
                    url=f"{page.full_url}?ajax=1&page={i + 1}&category={category.slug}",
                    headers={
                        "X-Requested-With": "XMLHttpRequest",
                    },
                )

    def request_filtering_video_category(self, site, page, limit):
        categories = VideoCategory.objects.in_site(site)

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
                    url=f"{page.full_url}?ajax=1&page={i + 1}&category={category.slug}",
                    headers={
                        "X-Requested-With": "XMLHttpRequest",
                    },
                )

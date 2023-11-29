import math

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import translation

from wagtail.models import Collection, Page, PageViewRestriction, Site

import requests
from requests import RequestException

from folioblog.blog.models import BlogCategory, BlogIndexPage, BlogPage
from folioblog.core.managers import qs_in_site_alt
from folioblog.core.models import FolioBlogSettings
from folioblog.gallery.models import GalleryPage
from folioblog.video.models import VideoCategory, VideoIndexPage, VideoPage


def get_requests_session():
    """Exists just to be mock by tests"""
    return requests.session()


def get_restriction_url(page, restriction):
    return page.get_site().root_url + reverse(
        "wagtailcore_authenticate_with_password",
        kwargs={
            "page_view_restriction_id": restriction.pk,
            "page_id": page.pk,
        },
    )


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = get_requests_session()
        self.requests_kwargs = {}

    def add_arguments(self, parser):
        parser.add_argument("--auth-user")
        parser.add_argument("--auth-passwd")

    def handle(self, *args, **options):
        # First clear the cache before rebuilding it!
        self.stdout.write(self.style.WARNING("WARNING: clearing cache...\n"))
        cache.clear()

        # Prepare request options for HTTP auth if needed.
        if options["auth_user"] and options["auth_passwd"]:  # pragma: no cover
            self.requests_kwargs["auth"] = (
                options["auth_user"],
                options["auth_passwd"],
            )

        # Then iterate over each sites to fetch their pages.
        for site in Site.objects.all():
            self.process_site(site, FolioBlogSettings.for_site(site))

    def process_site(self, site, folio_settings):
        self.stdout.write(self.style.WARNING(f"About requesting pages of site {site}:"))

        # Prevent duplicate restrictions already passed.
        restriction_passed = []

        # Fetch pages with translations to build renditions and page cache.
        qs = Page.objects.live().order_by("pk")
        qs = qs_in_site_alt(qs, site)
        for page in qs:
            # Check restriction first for private page.
            is_private, is_passed = self.process_private_page(page, restriction_passed)
            # Then fetch pages to build renditions and populate the cache!
            if not is_private or is_passed:
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

    def process_private_page(self, page, restriction_passed):
        is_private = False
        is_passed = False

        for restriction in page.get_view_restrictions():
            is_private = True
            if (
                restriction.restriction_type != PageViewRestriction.PASSWORD
            ):  # pragma: no cover
                continue

            is_passed = restriction in restriction_passed
            if not is_passed:
                if self.auth_private_page(page, restriction):
                    restriction_passed.append(restriction)
                    is_passed = True

        return is_private, is_passed

    def auth_private_page(self, page, restriction):
        # Build form POST url.
        domain = page.get_site().hostname
        url = get_restriction_url(page, restriction)

        # First fetch page to get/refresh CSRF token from cookies.
        self.request_page(page.full_url, method="get")

        csrf_token = self.session.cookies.get("csrftoken", domain=domain)
        if not csrf_token:
            self.stdout.write(
                self.style.WARNING(
                    f"Unable to fetch CSRF token for private page {page}"
                )
            )
            return False

        # Then post the password to store cookie session.
        self.request_page(
            url=url,
            method="post",
            data={
                "csrfmiddlewaretoken": csrf_token,
                "password": restriction.password,
                "return_url": page.url_path,
            },
            allow_redirects=False,  # No need to follow form redirection
        )

        session_id = self.session.cookies.get("sessionid", domain=domain)
        if not session_id:
            self.stdout.write(
                self.style.ERROR(f"Unable to auth for private page {page}")
            )
            return False

        return True

    def request_page(self, url, method="get", status=None, **kwargs):
        self.stdout.write(f'Requesting: {method.upper()} "{url}"')

        requests_kwargs = self.requests_kwargs | kwargs
        try:
            response = getattr(self.session, method)(url, **requests_kwargs)
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

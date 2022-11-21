import math

from django.core.cache import cache
from django.core.management.base import BaseCommand

from wagtail.models import Collection, Page, Site

import requests
from requests import RequestException

from folioblog.blog.models import BlogCategory, BlogPage
from folioblog.core.models import FolioBlogSettings
from folioblog.video.models import VideoCategory, VideoPage


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.requests_kwargs = {}

    def add_arguments(self, parser):
        parser.add_argument('--auth-user')
        parser.add_argument('--auth-passwd')

    def handle(self, *args, **options):
        site = Site.objects.get(is_default_site=True)
        folio_settings = FolioBlogSettings.load()

        if options['auth_user'] and options['auth_passwd']:  # pragma: no cover
            self.requests_kwargs['auth'] = (options['auth_user'], options['auth_passwd'])

        # First clear the cache before rebuilding it!
        self.stdout.write(self.style.WARNING('About clearing cache...'))
        cache.clear()

        # Then fetch pages to build renditions and populate the cache!
        qs = Page.objects.live().order_by('pk')
        for page in qs:
            if page.slug == 'root':
                continue

            # Request page without parameters.
            self.request_page(page.full_url)

            # Request pages with pagination only.
            if page.slug in ['posts', 'videos']:
                limit = folio_settings.video_pager_limit if page.slug == 'videos' else folio_settings.blog_pager_limit
                self.request_pagination(page, limit)

            # Request pages with pagination AND filtering.
            if page.slug == 'posts':
                self.request_filtering_blog_category(page, limit)
            if page.slug == 'videos':
                self.request_filtering_video_category(page, limit)
            elif page.slug == 'gallery':
                self.request_filtering_collection(page.full_url)

        # Don't forgot 404 page for renditions only (dummy url + not a 200 code)
        self.request_page(f'{site.root_url}/givemea404please', status=404)

        self.stdout.write(self.style.SUCCESS('\nAll page cache loaded.'))

    def request_page(self, full_url, status=None, **kwargs):
        self.stdout.write(f'Requesting: "{full_url}"')

        requests_kwargs = self.requests_kwargs | kwargs
        try:
            response = requests.get(full_url, **requests_kwargs)
        except RequestException as e:
            self.stdout.write(self.style.ERROR(f'Error on page {full_url} with exc {e}\n'))
        else:
            if (not status and not response.ok) or (status and status != response.status_code):
                self.stdout.write(self.style.WARNING(f'Error for page {full_url} with status {response.status_code}.\n'))  # noqa

    def request_pagination(self, page, limit):
        total = Page.objects.child_of(page).live().count()
        num_pages = math.ceil(total / limit)
        for i in range(0, num_pages):
            self.request_page(f'{page.full_url}?ajax=1&page={i + 1}', headers={
                'X-Requested-With': 'XMLHttpRequest',
            })

    def request_filtering_collection(self, full_url):
        root_collection = Collection.objects.get(name='Gallery')
        collections = Collection.objects.child_of(root_collection)

        for collection in collections:
            self.request_page(f'{full_url}?ajax=1&collection={collection.pk}', headers={
                'X-Requested-With': 'XMLHttpRequest',
            })

    def request_filtering_blog_category(self, page, limit):
        categories = BlogCategory.objects.all()

        for category in categories:
            total = BlogPage.objects.child_of(page).live().filter(category=category).count()
            num_pages = math.ceil(total / limit)

            for i in range(0, num_pages):
                self.request_page(f'{page.full_url}?ajax=1&page={i + 1}&category={category.slug}', headers={
                    'X-Requested-With': 'XMLHttpRequest',
                })

    def request_filtering_video_category(self, page, limit):
        categories = VideoCategory.objects.all()

        for category in categories:
            total = VideoPage.objects.child_of(page).live().filter(category=category).count()
            num_pages = math.ceil(total / limit)

            for i in range(0, num_pages):
                self.request_page(f'{page.full_url}?ajax=1&page={i + 1}&category={category.slug}', headers={
                    'X-Requested-With': 'XMLHttpRequest',
                })

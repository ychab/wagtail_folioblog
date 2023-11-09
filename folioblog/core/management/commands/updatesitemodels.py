from django.core.management.base import BaseCommand

from wagtail.models import Site

from folioblog.blog.models import BlogCategory, BlogPromote, BlogTag
from folioblog.core.models import Menu, Photographer
from folioblog.home.models import HomePage
from folioblog.video.models import VideoCategory, VideoPromote, VideoTag


class Command(BaseCommand):
    """
    One-shot commands to run after multi-tenant migrations (dear history!)
    """

    models = [
        # Blog
        BlogPromote,
        BlogCategory,
        BlogTag,
        # Core
        Menu,
        Photographer,
        # Video
        VideoPromote,
        VideoCategory,
        VideoTag,
    ]

    def add_arguments(self, parser):
        parser.add_argument("--site", help="Site ID to update", required=True)

    def handle(self, *args, **options):
        site = Site.objects.get(pk=options["site"])

        for Model in self.models:
            Model.objects.all().update(site=site)

        # Strangely, homepage could be affected by new migrations...
        for homepage in HomePage.objects.all():  # pragma: no cover
            revision = homepage.get_latest_revision()
            if revision and revision.content.get("menu_home"):
                revision.content["menu_home"][0][
                    "site"
                ] = site.pk  # Menu require a site ID
                revision.save()

        self.stdout.write(
            f'Site ({options["site"]}) have been set to all instance models'
        )

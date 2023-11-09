from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from wagtail.models import Site

from folioblog.blog.factories import (
    BlogCategoryFactory,
    BlogPromoteFactory,
    BlogTagFactory,
)
from folioblog.core.factories import MenuFactory
from folioblog.core.factories.images import PhotographerFactory
from folioblog.video.factories import (
    VideoCategoryFactory,
    VideoPromoteFactory,
    VideoTagFactory,
)


class UpdateSiteModelsCommandTestCase(TestCase):
    def test_update_site(self):
        site = Site.objects.get(is_default_site=True)
        new_site = Site.objects.get(is_default_site=True)

        instances = [
            BlogPromoteFactory(site=site),
            BlogCategoryFactory(site=site),
            BlogTagFactory(site=site),
            MenuFactory(site=site),
            PhotographerFactory(site=site),
            VideoPromoteFactory(site=site),
            VideoCategoryFactory(site=site),
            VideoTagFactory(site=site),
        ]

        out = StringIO()
        call_command("updatesitemodels", site=new_site.pk, stdout=out)

        for instance in instances:
            instance.refresh_from_db()
            self.assertEqual(instance.site, new_site, f"Instance {instance}")

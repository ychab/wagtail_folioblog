from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from wagtail.images import get_image_model
from wagtail.models import Site

from wagtail_factories import CollectionFactory, SiteFactory

from folioblog.core.factories import FolioBlogSettingsFactory, ImageFactory
from folioblog.core.models import FolioBlogSettings
from folioblog.gallery.templatetags.gallery import SPECS_LANDSCAPE, SPECS_PORTRAIT

Image = get_image_model()
Rendition = Image.get_rendition_model()


class GenerateRenditionsCommandTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)
        cls.root_collection = CollectionFactory()
        cls.child_collection = CollectionFactory(parent=cls.root_collection)

        site_settings = FolioBlogSettings.for_site(cls.site)
        site_settings.gallery_collection = cls.root_collection
        site_settings.save()

        cls.site_other = SiteFactory()
        FolioBlogSettingsFactory(site=cls.site_other, gallery_collection=None)

    def test_generate_rendition(self):
        # Landscape
        ImageFactory(
            collection=self.child_collection,
            file__width=500,
            file__height=300,
        )
        # Portrait
        ImageFactory(
            collection=self.child_collection,
            file__width=300,
            file__height=500,
        )
        count = len(SPECS_PORTRAIT) + len(SPECS_LANDSCAPE)

        out = StringIO()
        call_command("generaterenditions", stdout=out)
        self.assertIn(f"Skip generating renditions for site {self.site_other}", out.getvalue())
        self.assertIn(f"{count} renditions generated for site {self.site}", out.getvalue())

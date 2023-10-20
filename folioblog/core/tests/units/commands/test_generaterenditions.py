from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from wagtail.images import get_image_model

from folioblog.core.factories import ImageFactory
from folioblog.gallery.templatetags.gallery import GALLERY_SPECS

Image = get_image_model()
Rendition = Image.get_rendition_model()


class GenerateRenditionsCommandTestCase(TestCase):
    def tearDown(self):
        Image.objects.all().delete()

    def test_generate_rendition(self):
        ImageFactory()
        spec = list(GALLERY_SPECS.values())[0]

        out = StringIO()
        call_command("generaterenditions", stdout=out, specs=[spec])
        self.assertIn("About generating 1 renditions", out.getvalue())

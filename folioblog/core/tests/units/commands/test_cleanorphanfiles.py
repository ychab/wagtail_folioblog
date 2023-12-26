import shutil
from io import StringIO
from pathlib import Path
from tempfile import gettempdir

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase, override_settings

from wagtail.images import get_image_model

from folioblog.core.factories import ImageFactory

Image = get_image_model()


# To prevent collision with parallel test thread, use a specific dir for it.
@override_settings(MEDIA_ROOT=Path(gettempdir(), "folioblog-orphanfiles", "media"))
class CleanOrphanFilesCommandTestCase(TestCase):
    def tearDown(self):
        Image.objects.all().delete()
        shutil.rmtree(settings.MEDIA_ROOT / "original_images")

    def test_image_used(self):
        ImageFactory()

        out = StringIO()
        call_command("cleanorphanfiles", stdout=out)
        self.assertIn("0 orphan files deleted", out.getvalue())

    def test_image_orphans(self):
        image = ImageFactory()
        image.delete()

        out = StringIO()
        call_command("cleanorphanfiles", stdout=out)
        self.assertIn("1 orphan files deleted", out.getvalue())

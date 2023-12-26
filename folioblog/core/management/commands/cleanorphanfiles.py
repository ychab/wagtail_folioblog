from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from wagtail.images import get_image_model

Image = get_image_model()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--dir",
            default="original_images",
            help="Only one directory supported",
        )

    def handle(self, *args, **options):
        basepath = settings.MEDIA_ROOT / options["dir"]
        dirpath = Path(options["dir"])

        count = 0
        for file in basepath.iterdir():
            try:
                Image.objects.get(file=dirpath / file.name)
            except Image.DoesNotExist:
                file.unlink()
                count += 1

        self.stdout.write(self.style.SUCCESS(f"{count} orphan files deleted on drive."))

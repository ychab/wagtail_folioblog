import os

from django.conf import settings
from django.core.management.base import BaseCommand

from wagtail.images import get_image_model

Image = get_image_model()


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--dir', default='original_images')

    def handle(self, *args, **options):
        basepath = os.path.join(settings.MEDIA_ROOT, options['dir'])

        count = 0
        for subdir, dirs, files in os.walk(basepath):
            for file in files:
                try:
                    Image.objects.get(file=f'{options["dir"]}/{file}')
                except Image.DoesNotExist:
                    filepath = os.path.join(subdir, file)
                    os.remove(filepath)
                    count += 1

        self.stdout.write(self.style.SUCCESS(f'{count} orphan files deleted on drive.'))

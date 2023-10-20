from django.core.management.base import BaseCommand
from django.utils import timezone

from wagtail.images import get_image_model

from folioblog.gallery.templatetags.gallery import GALLERY_SPECS

Image = get_image_model()


class Command(BaseCommand):
    DEFAULT_SPECS = list(GALLERY_SPECS.values()) + []

    def add_arguments(self, parser):
        parser.add_argument("--specs", nargs="*", default=self.DEFAULT_SPECS)

    def handle(self, *args, **options):
        specs = options["specs"]
        time_start = timezone.now()

        qs = Image.objects.all().order_by("pk")
        count = qs.count()
        self.stdout.write(f"About generating {count} renditions...")

        for image in qs:
            for spec in specs:
                image.get_rendition(spec)

        time_end = timezone.now()
        time_total = time_end - time_start
        self.stdout.write(
            self.style.SUCCESS(f"Specs renditions generated in {time_total}")
        )

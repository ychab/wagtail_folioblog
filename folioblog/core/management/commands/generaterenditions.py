from django.core.management.base import BaseCommand

from wagtail.images import get_image_model
from wagtail.models import Collection, Site

from folioblog.core.models import FolioBlogSettings
from folioblog.gallery.templatetags.gallery import SPECS_LANDSCAPE, SPECS_PORTRAIT

Image = get_image_model()


class Command(BaseCommand):
    help = "Generate renditions for gallery page"

    def handle(self, *args, **options):
        sites = Site.objects.all()
        for site in sites:
            site_settings = FolioBlogSettings.for_site(site)
            if not site_settings.gallery_collection:
                self.stdout.write(
                    self.style.WARNING(f"Skip generating renditions for site {site}")
                )
                continue

            self.stdout.write(f"About generating renditions for site {site}")

            count = self.generate_site_renditions(site_settings.gallery_collection)

            self.stdout.write(
                self.style.SUCCESS(f"{count} renditions generated for site {site}")
            )

    def generate_site_renditions(self, root_collection):
        collection_qs = Collection.objects.descendant_of(root_collection)
        qs = Image.objects.filter(collection__in=collection_qs)

        count = 0
        for image in qs:
            specs = SPECS_PORTRAIT if image.is_portrait() else SPECS_LANDSCAPE
            for spec in specs.values():
                image.get_rendition(spec)
                count += 1

        return count

from django.core.management.base import BaseCommand

from wagtail.models import Site


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--hostname", default="127.0.0.1", required=True)
        parser.add_argument("--port", default=8000, required=True)

    def handle(self, *args, **options):
        site = Site.objects.get(is_default_site=True)
        site.hostname = options["hostname"]
        site.port = options["port"]
        site.save()

        self.stdout.write(
            f'Default site updated with hostname {options["hostname"]} and port {options["port"]}'
        )

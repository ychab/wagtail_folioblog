from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

from wagtail.models import Page, Site

from folioblog.core.utils.fixtures import fixtures_map

User = get_user_model()


class Command(BaseCommand):
    fixtures = fixtures_map

    def add_arguments(self, parser):
        parser.add_argument("action", choices=["dump", "load"])
        parser.add_argument("--reset", action="store_true", help="Just clean defaults pages and sites")

    def handle(self, action, *args, **options):
        if action == "load":
            if options["reset"]:
                # Just delete defaults created by Wagtail migration
                Page.objects.filter(slug="home", path="00010001").delete()
                Site.objects.filter(hostname="localhost", is_default_site=True).delete()

            call_command("loaddata", *self.fixtures.keys())
        else:
            for fixture, app_model in self.fixtures.items():
                app, label = app_model.split(".")
                # fmt: off
                if app in ["auth", "contenttypes", "taggit", "wagtailcore", "wagtailembeds"]:
                    app = "core"

                filepath = settings.BASE_DIR / "folioblog" / app / "fixtures" / f"{fixture}.json"
                # fmt: on

                kwargs = {
                    "indent": 4,
                    "output": filepath,
                }
                if fixture in ["pages", "blogpagetags", "videopagetags"]:
                    kwargs["natural_foreign"] = True

                self.stdout.write(f"Dump {app_model} > {filepath}")
                call_command("dumpdata", app_model, **kwargs)

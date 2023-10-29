from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from wagtail.models import Site


class UpdateSiteCommandTestCase(TestCase):
    def test_update_site(self):
        site = Site.objects.get(is_default_site=True)
        host = "example.fr"
        port = 8080
        out = StringIO()

        call_command("updatesite", site=site.pk, hostname=host, port=port, stdout=out)
        self.assertIn(
            f"Site ({site.pk}) updated with hostname {host} and port {port}",
            out.getvalue(),
        )

        site.refresh_from_db()
        self.assertEqual(site.hostname, host)
        self.assertEqual(site.port, port)

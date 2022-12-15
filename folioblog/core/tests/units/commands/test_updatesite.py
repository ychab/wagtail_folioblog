from io import StringIO

from django.core.management import call_command
from django.test import TestCase


class UpdateSiteCommandTestCase(TestCase):

    def test_update_site(self):
        host = 'example.fr'
        port = 8080
        out = StringIO()

        call_command('updatesite', hostname=host, port=port, stdout=out)
        self.assertIn(f'Default site updated with hostname {host} and port {port}', out.getvalue())

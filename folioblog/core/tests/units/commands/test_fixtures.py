from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import TestCase

from wagtail.models import Page, Site

from folioblog.core.utils.fixtures import fixtures_map


class FixturesCommandTestCase(TestCase):
    @mock.patch("folioblog.core.management.commands.fixtures.call_command")
    def test_load(self, mock_call_cmd):
        out = StringIO()
        call_command("fixtures", "load", stdout=out)
        self.assertEqual(mock_call_cmd.call_count, 1)
        self.assertEqual(mock_call_cmd.call_args.args[0], "loaddata")

    @mock.patch("folioblog.core.management.commands.fixtures.call_command")
    def test_load_reset(self, mock_call_cmd):
        page = Page.objects.get(slug="home")
        site = Site.objects.get(is_default_site=True)

        self.assertTrue(page)
        self.assertTrue(site)

        out = StringIO()
        call_command("fixtures", "load", reset=True, stdout=out)
        self.assertEqual(mock_call_cmd.call_count, 1)
        self.assertEqual(mock_call_cmd.call_args.args[0], "loaddata")

        with self.assertRaises(Page.DoesNotExist):
            page.refresh_from_db()

        with self.assertRaises(Site.DoesNotExist):
            site.refresh_from_db()

    @mock.patch("folioblog.core.management.commands.fixtures.call_command")
    def test_dump(self, mock_call_cmd):
        out = StringIO()
        call_command("fixtures", "dump", stdout=out)
        self.assertEqual(mock_call_cmd.call_count, len(fixtures_map))
        self.assertEqual(mock_call_cmd.call_args.args[0], "dumpdata")

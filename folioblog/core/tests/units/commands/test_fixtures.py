from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import TestCase

from folioblog.core.utils.fixtures import fixtures_map


class FixturesCommandTestCase(TestCase):
    @mock.patch("folioblog.core.management.commands.fixtures.call_command")
    def test_load(self, mock_call_cmd):
        out = StringIO()
        call_command("fixtures", "load", stdout=out)
        self.assertEqual(mock_call_cmd.call_count, 1)
        self.assertEqual(mock_call_cmd.call_args.args[0], "loaddata")

    @mock.patch("folioblog.core.management.commands.fixtures.call_command")
    def test_dump(self, mock_call_cmd):
        out = StringIO()
        call_command("fixtures", "dump", stdout=out)
        self.assertEqual(mock_call_cmd.call_count, len(fixtures_map))
        self.assertEqual(mock_call_cmd.call_args.args[0], "dumpdata")

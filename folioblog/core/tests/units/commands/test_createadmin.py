from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from folioblog.user.factories import UserFactory

User = get_user_model()


class CreateUserCommandTestCase(TestCase):
    def tearDown(self):
        User.objects.all().delete()

    def test_create_superuser(self):
        out = StringIO()
        extra_fields = {
            "username": "admin",
            "password": "foo",
            "email": "admin@example.com",
        }
        call_command("createadmin", stdout=out, **extra_fields)
        self.assertIn("Superuser created successfully.", out.getvalue())

        user = User.objects.get(username=extra_fields["username"])
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.email, extra_fields["email"])
        self.assertTrue(user.check_password(extra_fields["password"]))

    def test_update_superuser(self):
        out = StringIO()

        user = UserFactory(
            username="admin",
            email="admin@example.com",
            is_staff=False,
            is_superuser=False,
        )
        new_passwd = "bar"

        extra_fields = {
            "password": new_passwd,
        }
        call_command("createadmin", stdout=out, **extra_fields)
        user.refresh_from_db()

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password(new_passwd))
        self.assertIn("Superuser updated successfully.", out.getvalue())

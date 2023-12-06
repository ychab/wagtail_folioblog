from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--username", default="admin")
        parser.add_argument("--email", default="admin@example.com")
        parser.add_argument("--password", required=True)

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username=options["username"])
        except User.DoesNotExist:
            User.objects.create_superuser(
                username=options["username"],
                email=options["email"],
                password=options["password"],
            )
            self.stdout.write(self.style.SUCCESS("Superuser created successfully."))
        else:
            user.is_staff = True
            user.is_superuser = True
            user.email = options["email"]
            user.set_password(options["password"])
            user.save()
            self.stdout.write(self.style.SUCCESS("Superuser updated successfully."))

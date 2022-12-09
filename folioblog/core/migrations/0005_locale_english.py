from django.db import migrations


def initial_locale(apps, schema_editor):
    Locale = apps.get_model("wagtailcore.Locale")
    Locale.objects.get_or_create(language_code='en')


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_translatable"),
    ]

    operations = [
        migrations.RunPython(initial_locale, migrations.RunPython.noop),
    ]

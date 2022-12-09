# Generated by Django 4.1.3 on 2022-11-30 13:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0078_referenceindex'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='locale',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='wagtailcore.locale'),
        ),
        migrations.AddField(
            model_name='menu',
            name='translation_key',
            field=models.UUIDField(editable=False, null=True),
        ),
    ]

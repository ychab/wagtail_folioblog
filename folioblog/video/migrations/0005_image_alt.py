# Generated by Django 4.1.3 on 2022-11-30 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0004_translatable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videoindexpage',
            name='image_alt',
            field=models.CharField(blank=True, default='', max_length=512),
        ),
        migrations.AlterField(
            model_name='videopage',
            name='image_alt',
            field=models.CharField(blank=True, default='', max_length=512),
        ),
    ]
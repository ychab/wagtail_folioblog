# Generated by Django 4.2.7 on 2023-11-23 10:12

from django.db import migrations, models
import django.db.models.deletion
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0015_folioblogsettings_favicon"),
    ]

    operations = [
        migrations.AddField(
            model_name="folioblogsettings",
            name="image_404",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="folioblogsettings_not_found",
                to="core.folioimage",
                verbose_name="Image Not Found",
            ),
        ),
        migrations.AddField(
            model_name="folioblogsettings",
            name="text_404",
            field=wagtail.fields.StreamField(
                [
                    (
                        "items",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "language",
                                    wagtail.blocks.ChoiceBlock(
                                        choices=[
                                            ("en", "English"),
                                            ("fr", "French"),
                                            ("es", "Spanish"),
                                        ]
                                    ),
                                ),
                                (
                                    "title",
                                    wagtail.blocks.CharBlock(
                                        max_length=255, required=False
                                    ),
                                ),
                                (
                                    "subtitle",
                                    wagtail.blocks.CharBlock(
                                        max_length=255, required=False
                                    ),
                                ),
                                ("text", wagtail.blocks.TextBlock(required=False)),
                                (
                                    "link_text",
                                    wagtail.blocks.CharBlock(
                                        max_length=255, required=False
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                verbose_name="Text page not found",
                blank=True,
                null=True,
                use_json_field=True,
            ),
        ),
    ]

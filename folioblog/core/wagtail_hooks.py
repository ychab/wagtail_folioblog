import os.path

from django.utils.safestring import mark_safe
from django.utils.translation import gettext

import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail import hooks
from wagtail.admin.panels import FieldPanel
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    InlineStyleElementHandler,
)
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register,
)
from wagtail.embeds.models import Embed

from taggit.models import Tag

from folioblog.blog.models import BlogTag
from folioblog.video.models import VideoTag


@hooks.register('register_rich_text_features')
def register_keyboard_feature(features):
    # Just mimic wagtail.admin.wagtail_hooks.register_core_features()
    # @see draftjs_exporter.constants.py

    features.register_editor_plugin(
        "draftail",
        "keyboard",
        draftail_features.InlineStyleFeature(
            {
                "type": "KEYBOARD",
                "icon": "placeholder",
                "description": gettext("Keyboard"),
            }
        ),
    )
    features.register_converter_rule(
        "contentstate",
        "keyboard",
        {
            "from_database_format": {
                "kbd": InlineStyleElementHandler("KEYBOARD"),
            },
            "to_database_format": {"style_map": {"KEYBOARD": "kbd"}},
        },
    )


class TagModelAdmin(ModelAdmin):
    model = Tag
    menu_label = 'Tags'
    menu_icon = 'tag'
    list_display = ["name", "slug"]
    search_fields = ("name",)
    ordering = ('name',)
    panels = [FieldPanel('name')]  # only show the name field


class BlogTagModelAdmin(ModelAdmin):
    panels = [FieldPanel('name')]  # only show the name field
    model = BlogTag
    menu_label = 'Blog Tags'
    menu_icon = 'tag'
    list_display = ["name", "slug"]
    search_fields = ("name",)
    ordering = ('name',)


class VideoTagModelAdmin(ModelAdmin):
    panels = [FieldPanel('name')]  # only show the name field
    model = VideoTag
    menu_label = 'Video Tags'
    menu_icon = 'tag'
    list_display = ["name", "slug"]
    search_fields = ("name",)
    ordering = ('name',)


@modeladmin_register
class TagGroupAdmin(ModelAdminGroup):
    menu_label = 'Tags'
    menu_icon = 'tag'
    menu_order = 400
    items = (TagModelAdmin, BlogTagModelAdmin, VideoTagModelAdmin)


@modeladmin_register
class EmbedModelAdmin(ModelAdmin):
    model = Embed
    menu_label = 'Embeds'
    menu_icon = 'media'
    menu_order = 450
    list_display = ["title", "url_link", "thumbnail_link", "last_updated"]
    search_fields = ("title", "url")
    ordering = ('last_updated',)

    inspect_view_enabled = True

    panels = [
        FieldPanel("url"),
        FieldPanel("max_width"),
        FieldPanel("hash"),
        FieldPanel("type"),
        FieldPanel("html"),
        FieldPanel("title"),
        FieldPanel("author_name"),
        FieldPanel("provider_name"),
        FieldPanel("thumbnail_url"),
        FieldPanel("width"),
        FieldPanel("height"),
        FieldPanel("cache_until"),
    ]

    def url_link(self, obj):
        return mark_safe(
            f'<a href="{obj.url}" target="_blank">{obj.url}</a>'
        )
    url_link.short_description = 'URL'

    def thumbnail_link(self, obj):
        basename = os.path.basename(obj.thumbnail_url)
        return mark_safe(
            f'<a href="{obj.thumbnail_url}" target="_blank">{basename}</a>'
        )
    thumbnail_link.short_description = 'Thumbnail'

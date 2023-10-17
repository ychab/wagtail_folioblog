from django.utils.translation import gettext

import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail import hooks
from wagtail.admin.panels import FieldPanel
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    InlineStyleElementHandler,
)
from wagtail.embeds.models import Embed
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

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


class TagSnippetViewSet(SnippetViewSet):
    model = Tag
    menu_label = 'Tags'
    icon = 'tag'
    list_display = ["name", "slug"]
    search_fields = ("name",)
    ordering = ('name',)
    panels = [FieldPanel('name')]  # only show the name field


class BlogTagSnippetViewSet(SnippetViewSet):
    model = BlogTag
    menu_label = 'Blog Tags'
    icon = 'tag'
    list_display = ["name", "slug"]
    search_fields = ("name",)
    ordering = ('name',)
    panels = [FieldPanel('name')]  # only show the name field


class VideoTagSnippetViewSet(SnippetViewSet):
    model = VideoTag
    menu_label = 'Video Tags'
    icon = 'tag'
    list_display = ["name", "slug"]
    search_fields = ("name",)
    ordering = ('name',)
    panels = [FieldPanel('name')]  # only show the name field


@register_snippet
class TagSnippetViewSetGroup(SnippetViewSetGroup):
    menu_label = 'Tags'
    menu_icon = 'tag'
    menu_order = 400
    items = (TagSnippetViewSet, BlogTagSnippetViewSet, VideoTagSnippetViewSet)


@register_snippet
class EmbedSnippetViewSet(SnippetViewSet):
    add_to_admin_menu = True
    model = Embed
    menu_label = 'Embeds'
    icon = 'media'
    menu_order = 450
    list_display = ["title", "url", "thumbnail_url", "last_updated"]
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

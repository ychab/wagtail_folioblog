from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail import hooks
from wagtail.admin.filters import WagtailFilterSet
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    InlineStyleElementHandler,
)
from wagtail.admin.widgets.slug import SlugInput
from wagtail.embeds.models import Embed
from wagtail.models import Site
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

import django_filters

from folioblog.core.models import Menu, Photographer


@hooks.register("register_rich_text_features")
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


class MultiSiteFilterSet(WagtailFilterSet):
    site = django_filters.ModelChoiceFilter(queryset=Site.objects.all())


class SnippetViewSetMultiSiteMixin:
    filterset_class = MultiSiteFilterSet

    panels = [
        FieldPanel("site"),
    ]

    def get_queryset(self, request):
        qs = self.model.objects.all()
        qs = qs.select_related("site")
        return qs


class SnippetViewSetI18nMultiSiteMixin(SnippetViewSetMultiSiteMixin):
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("locale")


class BaseTagSnippetViewSet(SnippetViewSetMultiSiteMixin, SnippetViewSet):
    icon = "tag"

    list_display = ["name", "slug", "site"]
    search_fields = ("name",)
    ordering = ("site", "name")

    panels = [
        FieldPanel("name"),
    ] + SnippetViewSetI18nMultiSiteMixin.panels


class BaseCategorySnippetViewSet(SnippetViewSetI18nMultiSiteMixin, SnippetViewSet):
    icon = "folder-open-1"

    list_display = ["name", "slug", "locale", "site"]
    search_fields = ("name", "slug")
    ordering = ("site", "name")

    panels = [
        FieldPanel("name"),
        FieldPanel("slug", widget=SlugInput),  # @todo - broken feature?
    ] + SnippetViewSetI18nMultiSiteMixin.panels


class BasePromoteSnippetViewSet(SnippetViewSetI18nMultiSiteMixin, SnippetViewSet):
    icon = "table"

    list_display = ["title", "link_more", "locale", "site"]
    search_fields = ("title",)
    ordering = ("title",)

    panels = [
        FieldPanel("title"),
        FieldPanel("link_more"),
        InlinePanel("related_links", label=_("Related links")),
    ] + SnippetViewSetI18nMultiSiteMixin.panels


class MenuSnippetViewSet(SnippetViewSetI18nMultiSiteMixin, SnippetViewSet):
    model = Menu
    icon = "bars"

    list_display = ["name", "homepage", "is_active", "locale", "site"]
    search_fields = ("name",)
    ordering = ("name",)

    panels = [
        FieldPanel("name"),
        FieldPanel("homepage"),
        FieldPanel("is_active"),
        InlinePanel("links", label=_("Links")),
    ] + SnippetViewSetI18nMultiSiteMixin.panels

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("homepage")
        return qs


class PhotographerSnippetViewSet(SnippetViewSetI18nMultiSiteMixin, SnippetViewSet):
    model = Photographer
    icon = "crosshairs"

    list_display = ["name", "website", "locale", "site"]
    search_fields = ("name",)
    ordering = ("name",)

    panels = [
        FieldPanel("name"),
        FieldPanel("website"),
    ] + SnippetViewSetI18nMultiSiteMixin.panels


class EmbedSnippetViewSet(SnippetViewSet):
    model = Embed
    icon = "media"

    list_display = ["title", "url", "thumbnail_url", "last_updated"]
    search_fields = ("title", "url")
    ordering = ("last_updated",)

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


register_snippet(EmbedSnippetViewSet)
register_snippet(MenuSnippetViewSet)
register_snippet(PhotographerSnippetViewSet)

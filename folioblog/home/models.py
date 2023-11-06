from django.db.models import Prefetch
from django.utils.translation import get_language

from folioblog.blog.models import BlogPromote, BlogPromoteLink
from folioblog.core.models import BaseIndexPage, FolioBlogSettings
from folioblog.video.models import VideoPromote, VideoPromoteLink


class HomePage(BaseIndexPage):
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        folio_settings = FolioBlogSettings.for_request(request)
        lang_code = get_language()

        context["blog_snippet"] = (
            BlogPromote.objects.in_site(folio_settings.site)
            .filter_language()
            .prefetch_related(
                Prefetch(
                    "related_links",
                    queryset=BlogPromoteLink.objects.filter(
                        related_page__live=True,
                        related_page__locale__language_code=lang_code,
                    )
                    .select_related("related_page__category", "related_page__image")
                    .prefetch_related("related_page__image__renditions")
                    .order_by("sort_order"),
                )
            )
            .order_by("-pk")
            .first()
        )

        context["video_snippet"] = (
            VideoPromote.objects.in_site(folio_settings.site)
            .filter_language()
            .prefetch_related(
                Prefetch(
                    "related_links",
                    queryset=VideoPromoteLink.objects.filter(
                        related_page__live=True,
                        related_page__locale__language_code=lang_code,
                    )
                    .select_related("related_page__thumbnail")
                    .prefetch_related("related_page__thumbnail__renditions")
                    .order_by("sort_order"),
                )
            )
            .order_by("-pk")
            .first()
        )

        return context

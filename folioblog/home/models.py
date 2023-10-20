from django.db.models import Prefetch
from django.utils.translation import get_language

from folioblog.blog.models import BlogPromote, BlogPromoteLink
from folioblog.core.models import BaseIndexPage
from folioblog.video.models import VideoPromote, VideoPromoteLink


class HomePage(BaseIndexPage):
    parent_page_types = ["portfolio.PortfolioPage"]
    subpage_types = []

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        lang_code = get_language()

        context["blog_snippet"] = (
            BlogPromote.objects.filter_language()
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
            .first()
        )

        context["video_snippet"] = (
            VideoPromote.objects.filter_language()
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
            .first()
        )

        return context

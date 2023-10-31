from django.views.generic import TemplateView

from folioblog.blog.models import BlogIndexPage, BlogPage
from folioblog.core.models import FolioBlogSettings
from folioblog.core.utils import get_block_language


class RssView(TemplateView):
    template_name = "core/rss.xml"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["feed_active"] = False

        folio_settings = FolioBlogSettings.for_request(self.request)
        rss_feed = get_block_language(folio_settings.rss_feed) or {}

        if rss_feed:
            root_page = folio_settings.site.root_page.localized

            qs = (
                BlogPage.objects.live()
                .descendant_of(root_page)
                .filter_language()
                .select_related("image")
                .prefetch_related("image__renditions")
                .defer_streamfields()
                .order_by("-date")[: rss_feed.get("limit", 50)]
            )

            context["feed_active"] = True
            context["feed_title"] = rss_feed.get("title", "RSS feed")
            context["feed_description"] = rss_feed.get("description", "")
            context["blog_index"] = (
                BlogIndexPage.objects.descendant_of(root_page).filter_language().first()
            )

            context["feed_items"] = []
            for post in qs:
                context["feed_items"].append(post)

        return context

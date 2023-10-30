from django.views.generic import TemplateView

from folioblog.blog.models import BlogIndexPage, BlogPage
from folioblog.core.models import FolioBlogSettings
from folioblog.core.utils import get_block_language


class RssView(TemplateView):
    template_name = "core/rss.xml"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        folio_settings = FolioBlogSettings.for_request(self.request)
        rss_feed = get_block_language(folio_settings.rss_feed)

        qs = (
            BlogPage.objects.live()
            .select_related("image")
            .prefetch_related("image__renditions")
            .filter_language()
            .defer_streamfields()
            .order_by("-date")[: rss_feed["limit"]]
        )

        context["feed_title"] = rss_feed["title"]
        context["feed_description"] = rss_feed["description"]
        context["blog_index"] = BlogIndexPage.objects.filter_language().first()
        context["feed_items"] = []

        for post in qs:
            context["feed_items"].append(post)

        return context

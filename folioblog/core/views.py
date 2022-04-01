from django.views.generic import TemplateView

from folioblog.blog.models import BlogPage
from folioblog.core.models import FolioBlogSettings


class RssView(TemplateView):
    template_name = 'core/rss.xml'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        folio_settings = FolioBlogSettings.load(request_or_site=self.request)

        context['feed_title'] = folio_settings.rss_title
        context['feed_description'] = folio_settings.rss_description

        qs = BlogPage.objects.live().order_by('-date')[:folio_settings.rss_limit]
        qs = qs.select_related('image').prefetch_related('image__renditions')

        context['feed_items'] = []
        for post in qs:
            context['feed_items'].append({
                'title': post.title,
                'link': post.get_full_url(self.request),
                'description': post.intro,
                'date': post.date,
                'image': post.image,
                'category': post.category,
            })

        return context

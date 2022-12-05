from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images import get_image_model
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TagBase, TaggedItemBase

from folioblog.core.models import (
    BaseCategory, BaseIndexPage, BasePage, FolioBlogSettings,
)
from folioblog.core.pagination import FolioBlogPaginator

Image = get_image_model()


class BlogIndexPage(BaseIndexPage):
    ajax_template = 'blog/blog_index_item.html'

    parent_page_types = ['portfolio.PortfolioPage']
    subpage_types = ['blog.BlogPage']

    def serve(self, request, *args, **kwargs):
        response = super().serve(request, *args, **kwargs)
        response.headers['Link'] = f'<{self.get_full_url(request)}>; rel="canonical"'
        return response

    def get_context(self, request, *args, **kwargs):
        folio_settings = FolioBlogSettings.load(request_or_site=request)
        context = super().get_context(request, *args, **kwargs)

        categories = BlogCategory.objects.all().order_by('slug')
        context['categories'] = categories
        context['category_filters'] = [{'name': str(c), 'value': c.slug} for c in categories]
        context['category_query'] = request.GET.get('category', '')

        qs = BlogPage.objects.live()
        qs = qs.select_related('category', 'image')
        qs = qs.prefetch_related('image__renditions')
        qs = qs.order_by('-date', '-pk')
        if request.GET.get('category'):
            qs = qs.filter(category__slug=request.GET['category'])

        paginator = FolioBlogPaginator(qs, folio_settings.blog_pager_limit)
        context['blogpages'] = paginator.get_page(request.GET.get('page'))

        return context


class BlogTag(TagBase):
    pass


class BlogPageTag(TaggedItemBase):
    tag = models.ForeignKey(BlogTag, on_delete=models.CASCADE, related_name="tagged_blogs")
    content_object = ParentalKey('BlogPage', on_delete=models.CASCADE, related_name='tagged_items')


@register_snippet
class BlogCategory(BaseCategory):

    class Meta:
        verbose_name_plural = 'blog categories'


class BlogPage(BasePage):
    date = models.DateField(_('Date de publication'))

    image_body = models.ForeignKey(
        Image,
        on_delete=models.PROTECT,
        related_name='blog_body',
        null=True,
        blank=True,
    )

    blockquote = models.TextField(blank=True, default='')
    blockquote_author = models.CharField(max_length=128, blank=True, default='')
    blockquote_ref = models.CharField(max_length=128, blank=True, default='')

    category = models.ForeignKey(BlogCategory, on_delete=models.PROTECT, related_name='blogpages')
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)

    search_fields = Page.search_fields + [
        index.AutocompleteField('subheading'),
        index.SearchField('subheading'),
        index.SearchField('intro'),
        index.SearchField('body'),
        index.FilterField('category_id'),
        # Unfortunetly, doesn't work yet for filtering but still indexed
        # @see https://docs.wagtail.org/en/stable/topics/search/indexing.html#index-relatedfields
        index.RelatedFields('tags', [
            index.FilterField('slug'),
        ]),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('date'),
                FieldPanel('tags'),
                FieldPanel('category', widget=forms.Select),
            ],
            heading=_("Blog information"),
        ),
        FieldPanel('subheading'),
        FieldPanel('intro'),
        FieldPanel('body', classname="full"),
        MultiFieldPanel(
            [
                FieldPanel('blockquote'),
                FieldPanel('blockquote_author'),
                FieldPanel('blockquote_ref'),
            ],
            heading=_("Citation"),
        ),
        MultiFieldPanel(
            [
                FieldPanel('image'),
                FieldPanel('image_body'),
                FieldPanel('image_alt'),
            ],
            heading=_("Image"),
        ),
        InlinePanel('related_links', label=_('Related links')),
    ]

    parent_page_types = ['blog.BlogIndexPage']
    subpage_types = []


class BlogPageRelatedLink(Orderable):
    page = ParentalKey(BlogPage, related_name='related_links')
    related_page = ParentalKey(Page, related_name='blog_related_pages')

    panels = [
        FieldPanel('related_page'),
    ]


@register_snippet
class BlogPromote(ClusterableModel):
    title = models.CharField(max_length=255)
    link_more = models.CharField(max_length=255)

    panels = [
        FieldPanel('title'),
        FieldPanel('link_more'),
        InlinePanel('related_links', label=_('Related links')),
    ]

    def __str__(self):
        return self.title


class BlogPromoteLink(Orderable):
    snippet = ParentalKey(BlogPromote, related_name='related_links')
    related_page = ParentalKey(BlogPage, related_name='promoted_links')

    panels = [
        FieldPanel('related_page'),
    ]

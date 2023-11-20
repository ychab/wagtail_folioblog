from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images import get_image_model
from wagtail.models import Orderable, Page, TranslatableMixin
from wagtail.search import index

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TagBase, TaggedItemBase

from folioblog.core.managers import I18nMultiSiteManager
from folioblog.core.models import (
    BaseCategory,
    BaseIndexPage,
    BasePage,
    FolioBlogSettings,
    MultiSiteMixin,
)
from folioblog.core.pagination import FolioBlogPaginator

Image = get_image_model()


class BlogIndexPage(BaseIndexPage):
    ajax_template = "blog/blog_index_item.html"

    parent_page_types = ["home.HomePage"]
    subpage_types = ["blog.BlogPage"]

    def get_context(self, request, *args, **kwargs):
        folio_settings = FolioBlogSettings.for_request(request)
        context = super().get_context(request, *args, **kwargs)

        categories = (
            BlogCategory.objects.in_site(folio_settings.site)
            .filter_language()
            .order_by("slug")
        )

        context["categories"] = categories
        context["category_filters"] = [
            {"name": str(c), "value": c.slug} for c in categories
        ]
        context["category_query"] = request.GET.get("category", "")

        qs = BlogPage.objects.live().child_of(self).filter_language()
        if request.GET.get("category"):
            qs = qs.filter(category__slug=request.GET["category"])
        qs = qs.select_related("category", "image")
        qs = qs.prefetch_related("image__renditions")
        qs = qs.order_by("-date", "-pk")

        paginator = FolioBlogPaginator(qs, folio_settings.blog_pager_limit)
        context["blogpages"] = paginator.get_page(request.GET.get("page"))

        return context


class BlogTag(MultiSiteMixin, TagBase):
    pass


class BlogPageTag(TaggedItemBase):
    tag = models.ForeignKey(
        BlogTag, on_delete=models.CASCADE, related_name="tagged_blogs"
    )
    content_object = ParentalKey(
        "BlogPage", on_delete=models.CASCADE, related_name="tagged_items"
    )


class BlogCategory(BaseCategory):
    class Meta(BaseCategory.Meta):
        verbose_name_plural = "blog categories"


class BlogPage(BasePage):
    date = models.DateField(_("Date de publication"))

    image_body = models.ForeignKey(
        Image,
        on_delete=models.PROTECT,
        related_name="blog_body",
        null=True,
        blank=True,
    )

    blockquote = models.TextField(blank=True, default="")
    blockquote_author = models.CharField(max_length=128, blank=True, default="")
    blockquote_ref = models.CharField(max_length=128, blank=True, default="")

    category = models.ForeignKey(
        BlogCategory, on_delete=models.PROTECT, related_name="blogpages"
    )
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)

    search_fields = Page.search_fields + [
        index.AutocompleteField("subheading"),
        index.SearchField("subheading"),
        index.SearchField("intro"),
        index.SearchField("body"),
        index.FilterField("category_id"),
        index.FilterField("locale_id"),
        # Unfortunetly, doesn't work yet for filtering but still indexed
        # @see https://docs.wagtail.org/en/stable/topics/search/indexing.html#index-relatedfields
        index.RelatedFields(
            "tags",
            [
                index.FilterField("slug"),
            ],
        ),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("date"),
                FieldPanel("tags"),
                FieldPanel("category"),
            ],
            heading=_("Blog information"),
        ),
        FieldPanel("subheading"),
        FieldPanel("intro"),
        FieldPanel("body", classname="full"),
        MultiFieldPanel(
            [
                FieldPanel("blockquote"),
                FieldPanel("blockquote_author"),
                FieldPanel("blockquote_ref"),
            ],
            heading=_("Citation"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("image"),
                FieldPanel("image_body"),
                FieldPanel("image_alt"),
            ],
            heading=_("Image"),
        ),
        InlinePanel("related_links", label=_("Related links")),
    ]

    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []


class BlogPageRelatedLink(Orderable):
    page = ParentalKey(BlogPage, related_name="related_links")
    related_page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="blog_related_pages",
    )

    panels = [
        FieldPanel("related_page"),
    ]


class BlogPromote(MultiSiteMixin, TranslatableMixin, ClusterableModel):
    title = models.CharField(max_length=255)
    link_more = models.CharField(max_length=255)

    objects = I18nMultiSiteManager()

    class Meta(TranslatableMixin.Meta):
        pass

    def __str__(self):
        return self.title


class BlogPromoteLink(Orderable):
    snippet = ParentalKey(BlogPromote, related_name="related_links")
    related_page = models.ForeignKey(
        BlogPage,
        on_delete=models.CASCADE,
        related_name="promoted_links",
    )

    panels = [
        FieldPanel("related_page"),
    ]

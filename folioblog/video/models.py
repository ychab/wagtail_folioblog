import logging
from io import BytesIO

from django.core.files.images import ImageFile
from django.db import models
from django.db.models import Prefetch
from django.utils.functional import cached_property

from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.embeds import embeds
from wagtail.embeds.exceptions import EmbedException
from wagtail.images import get_image_model
from wagtail.models import Collection, Orderable, Page, TranslatableMixin
from wagtail.search import index

import requests
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
logger = logging.getLogger(__name__)


class VideoIndexPage(BaseIndexPage):
    ajax_template = "video/video_index_grid_item.html"

    subpage_types = ["video.VideoPage"]

    def get_context(self, request, *args, **kwargs):
        folio_settings = FolioBlogSettings.for_request(request)
        context = super().get_context(request, *args, **kwargs)

        categories = (
            VideoCategory.objects.in_site(folio_settings.site)
            .filter(videopages__isnull=False)
            .filter_language()
            .order_by("slug")
            .distinct()
        )
        context["categories"] = categories
        context["category_filters"] = [{"name": str(c), "value": c.slug} for c in categories]
        context["category_query"] = request.GET.get("category", "")

        qs = (
            VideoPage.objects.child_of(self)
            .live()
            .filter_language()
            .select_related("category")
            .prefetch_related(
                "image__renditions",
                "thumbnail__renditions",
                Prefetch(
                    "tagged_items",
                    queryset=VideoPageTag.objects.select_related("tag").all(),
                ),
            )
            .order_by("-date", "-pk")
        )
        if request.GET.get("category"):
            qs = qs.filter(category__slug=request.GET["category"])

        paginator = FolioBlogPaginator(qs, folio_settings.video_pager_limit)
        context["videos"] = paginator.get_page(request.GET.get("page"))

        return context


class VideoCategory(BaseCategory):
    class Meta(BaseCategory.Meta):
        verbose_name_plural = "video categories"


class VideoTag(MultiSiteMixin, TagBase):
    pass


class VideoPageTag(TaggedItemBase):
    tag = models.ForeignKey(VideoTag, on_delete=models.CASCADE, related_name="tagged_videos")
    content_object = ParentalKey("VideoPage", on_delete=models.CASCADE, related_name="tagged_items")


class VideoPage(BasePage):
    date = models.DateField("Publish date")
    author = models.CharField(max_length=256, blank=True, default="")

    video_url = models.URLField()
    thumbnail = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Thumbnail",
        related_name="videos",
    )

    category = models.ForeignKey(VideoCategory, on_delete=models.PROTECT, related_name="videopages")
    tags = ClusterTaggableManager(through=VideoPageTag, blank=True)

    api_fields = BasePage.api_fields + [
        APIField("date"),
        APIField("author"),
        APIField("video_url"),
        APIField("thumbnail"),
        APIField("category"),
        APIField("tags"),
    ]

    search_fields = Page.search_fields + [
        index.AutocompleteField("subheading"),
        index.SearchField("subheading"),
        index.SearchField("intro"),
        index.SearchField("body"),
        index.FilterField("category_id"),
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
        FieldPanel("subheading"),
        MultiFieldPanel(
            [
                FieldPanel("date"),
                FieldPanel("author"),
                FieldPanel("category"),
                FieldPanel("tags"),
            ],
            heading="Video information",
        ),
        FieldPanel("intro"),
        FieldPanel("body", classname="full"),
        MultiFieldPanel(
            [
                FieldPanel("image"),
                FieldPanel("image_alt"),
            ],
            heading="Image",
        ),
        FieldPanel("video_url"),
        FieldPanel("thumbnail"),
        InlinePanel("related_links", label="Related pages"),
    ]

    parent_page_types = ["video.VideoIndexPage"]
    subpage_types = []

    @cached_property
    def video_id(self):
        # For now, keep it simple, stupid!
        if "watch?v=" in self.video_url:  # pragma: no branch
            return self.video_url.split("=")[-1]

    @cached_property
    def embed(self):
        try:
            return embeds.get_embed(self.video_url)
        except EmbedException as exc:
            logger.exception(f"Embed error for page {self.pk} with src {self.video_url} and error msg: {exc}")

    def save_revision(self, *args, **kwargs):
        if self.thumbnail is None:
            self.thumbnail = self.extract_thumbnail()
        return super().save_revision(*args, **kwargs)

    def extract_thumbnail(self):
        try:
            r = requests.get(self.embed.thumbnail_url)
        except requests.RequestException as exc:
            logger.exception(f"Error thumbnail for page {self.pk} with exc: {exc}")
            return
        else:
            if not r.ok:
                logger.warning(f"Bad status thumbnail {r.status_code} for page {self.pk}")
                return

        ext = self.embed.thumbnail_url.split(".")[-1]

        thumbnail = Image(
            title=self.embed.title,
            file=ImageFile(
                file=BytesIO(r.content),
                name=f"thumbnail-{self.video_id}.{ext}",
            ),
            collection=Collection.objects.get(name="Video thumbnail"),
        )
        thumbnail.save()
        return thumbnail


class VideoPageRelatedLink(Orderable):
    page = ParentalKey(VideoPage, related_name="related_links")
    related_page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="video_related_pages",
    )

    panels = [
        FieldPanel("related_page"),
    ]


class VideoPromote(MultiSiteMixin, TranslatableMixin, ClusterableModel):
    title = models.CharField(max_length=255)
    link_more = models.CharField(max_length=255)

    objects = I18nMultiSiteManager()

    class Meta(TranslatableMixin.Meta):
        pass

    def __str__(self):
        return self.title

    @cached_property
    def first_video(self):
        link = self.related_links.first()
        return link.related_page if link else None


class VideoPromoteLink(Orderable):
    snippet = ParentalKey(VideoPromote, related_name="related_links")
    related_page = models.ForeignKey(
        VideoPage,
        on_delete=models.CASCADE,
        related_name="promoted_links",
    )

    panels = [
        FieldPanel("related_page"),
    ]

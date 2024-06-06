from pathlib import Path

from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import get_language

from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.api import APIField
from wagtail.contrib.settings.models import BaseSiteSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.fields import RichTextField, StreamField
from wagtail.images.api.v2.serializers import ImageDownloadUrlField
from wagtail.images.models import AbstractImage, AbstractRendition, Image, ImageQuerySet
from wagtail.models import Collection, Orderable, Page, Site, TranslatableMixin

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from folioblog.core.blocks import CookieBannersBlock, PageNotFoundsBlock, RssFeedsBlock
from folioblog.core.managers import (
    I18nMultiSiteManager,
    I18nPageManager,
    ImageManager,
    MultiSiteManager,
)
from folioblog.core.sitemap import SitemapPageMixin


class MultiSiteMixin(models.Model):
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        db_index=True,
        related_name="%(app_label)s_%(class)s",
        related_query_name="%(app_label)s_%(class)ss",
    )

    objects = MultiSiteManager()

    class Meta:
        abstract = True


class Photographer(MultiSiteMixin, models.Model):
    name = models.CharField(max_length=255, blank=True)
    website = models.URLField(null=True, blank=True)

    api_fields = [
        APIField("name"),
        APIField("website"),
    ]

    def __str__(self):
        return self.name


class FolioImage(AbstractImage):
    caption = models.CharField(max_length=255, blank=True)
    photographer = models.ForeignKey(Photographer, on_delete=models.SET_NULL, null=True, blank=True)

    admin_form_fields = Image.admin_form_fields + (
        "caption",
        "photographer",
    )

    objects = ImageManager.from_queryset(ImageQuerySet)()

    api_fields = [
        APIField("title"),
        APIField("width"),
        APIField("height"),
        APIField("caption"),
        APIField("photographer"),
        APIField("download_url", serializer=ImageDownloadUrlField(read_only=True)),
    ]

    @property
    def default_alt_text(self):
        # @todo - @fixme - unfortunetly, image translation is not supported yet...
        language_code = get_language()
        if language_code == settings.LANGUAGE_CODE:
            return self.caption or self.title
        else:
            return ""

    def figcaption(self, alt_text=None):
        alt_text = alt_text or self.default_alt_text

        output = f"<cite>{alt_text}</cite> - " if alt_text else ""
        if self.photographer:
            output += "&copy; "
            if self.photographer.website:
                output += f'<a href="{self.photographer.website}" target="_blank">{self.photographer}</a>'
            else:
                output += f"{self.photographer}"

        return mark_safe(output)

    def save(self, *args, **kwargs):
        original = self._meta.model.objects.get(pk=self.pk) if self.pk else None
        super().save(*args, **kwargs)

        if original and self.collection != original.collection:
            Rendition = self.get_rendition_model()
            qs = Rendition.objects.filter(image=self)
            for rendition in qs:
                rendition.delete()
                self.get_rendition(rendition.filter_spec)


class FolioRendition(AbstractRendition):
    image = models.ForeignKey(FolioImage, on_delete=models.CASCADE, related_name="renditions")

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)

    def get_upload_to(self, filename):
        # No hash in filename? (i.e: no focal point)
        if filename.count(".") == 2:
            name, spec, ext = filename.split(".")
            filename = f"{name}.{ext}"
        else:
            # Fill images spec support focal point so they needs a hash(?)
            name, hash, *spec, ext = filename.split(".")
            spec = ".".join(spec)
            filename = f"{name}.{hash}.{ext}"

        filename = self.file.field.storage.get_valid_name(filename)
        return Path("images", slugify(self.image.collection), spec, filename)


class BaseCategory(MultiSiteMixin, TranslatableMixin, models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    objects = I18nMultiSiteManager()

    api_fields = [
        APIField("name"),
        APIField("slug"),
    ]

    class Meta(TranslatableMixin.Meta):
        abstract = True
        unique_together = TranslatableMixin.Meta.unique_together + [
            (
                "locale",
                "slug",
                "site",
            ),  # TranslatableMixin.check() don't allow us to mix it!
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BaseIndexPage(SitemapPageMixin, Page):
    subheading = models.CharField(max_length=512, blank=True, default="")

    image = models.ForeignKey(
        FolioImage,
        on_delete=models.PROTECT,
        verbose_name="Image",
        related_name="%(app_label)s_%(class)s_+",
        related_query_name="%(app_label)s_%(class)ss",
    )
    image_alt = models.CharField(max_length=512, blank=True, default="")

    api_fields = [
        APIField("subheading"),
        APIField("image"),
        APIField("image_alt"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("subheading"),
        MultiFieldPanel(
            [
                FieldPanel("image"),
                FieldPanel("image_alt"),
            ],
            heading="Image",
        ),
    ]

    objects = I18nPageManager()

    class Meta:
        abstract = True

    @property
    def caption(self):
        return self.image_alt or self.image.default_alt_text

    @property
    def seo_description(self):
        return self.search_description

    def get_translations(self, inclusive=False):
        # Translation queryset would be later chained with .only / .defer() and
        # thus, will break because we massively inject select_related() + prefetch_related()
        # in custom manager (i.e: I18nIndexPageManager).
        qs = super().get_translations(inclusive=inclusive)
        qs = qs.select_related(None)
        qs = qs.prefetch_related(None)
        return qs


class BasePage(BaseIndexPage):
    intro = models.TextField(default="", blank=True)
    body = RichTextField(blank=True)

    api_fields = BaseIndexPage.api_fields + [
        APIField("intro"),
        APIField("body"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("subheading"),
        FieldPanel("intro"),
        FieldPanel("body", classname="full"),
        MultiFieldPanel(
            [
                FieldPanel("image"),
                FieldPanel("image_alt"),
            ],
            heading="Image",
        ),
    ]

    class Meta:
        abstract = True

    @property
    def seo_description(self):
        return self.intro or self.search_description


class BasicPage(BasePage):
    subpage_types = []

    content_panels = BasePage.content_panels + [
        InlinePanel("related_links", label="Related links"),
    ]


class BasicPageRelatedLink(Orderable):
    page = ParentalKey(BasicPage, related_name="related_links")
    related_page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="basic_related_pages",
    )

    panels = [
        FieldPanel("related_page"),
    ]


@register_setting(icon="cog")
class FolioBlogSettings(BaseSiteSetting):
    # @see https://docs.wagtail.org/en/stable/reference/contrib/settings.html#utilising-select-related-to-improve-efficiency  # noqa
    select_related = ["gallery_collection", "image_password", "image_404"]

    favicon = models.ImageField(upload_to="favicons", blank=True, default="")
    image_password = models.ForeignKey(
        FolioImage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Image password",
        related_name="folioblogsettings_pwd",
    )
    image_404 = models.ForeignKey(
        FolioImage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Image Not Found",
        related_name="folioblogsettings_not_found",
    )
    text_404 = StreamField(
        PageNotFoundsBlock(),
        verbose_name="Text page not found",
        null=True,
        blank=True,
        use_json_field=True,
    )

    google_analytics_id = models.CharField(
        verbose_name="Google Analytics ID",
        max_length=128,
        blank=True,
        default="",
    )
    author = models.CharField(
        verbose_name="Meta author",
        max_length=128,
        blank=True,
        default="",
    )

    linkedin_url = models.URLField(blank=True, default="")
    github_url = models.URLField(blank=True, default="")
    instagram_url = models.URLField(blank=True, default="")
    facebook_url = models.URLField(blank=True, default="")
    twitter_url = models.URLField(blank=True, default="")
    twitter_site = models.CharField(max_length=255, blank=True, default="")
    twitter_creator = models.CharField(max_length=255, blank=True, default="")

    email = models.EmailField(
        help_text="Adresse email utilisé Email address used for contact form submission.",
        blank=True,
        default="",
    )
    phone = models.CharField(max_length=128, blank=True, default="")

    cookie_banner = StreamField(
        CookieBannersBlock(),
        null=True,
        blank=True,
        use_json_field=True,
    )

    rss_feed = StreamField(
        RssFeedsBlock(),
        null=True,
        blank=True,
        use_json_field=True,
    )

    blog_pager_limit = models.PositiveSmallIntegerField(default=8)
    video_pager_limit = models.PositiveSmallIntegerField(default=10)

    gallery_collection = models.ForeignKey(
        Collection,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    search_limit = models.PositiveSmallIntegerField(default=10)
    search_operator = models.CharField(
        max_length=3,
        choices=[("or", "Or"), ("and", "And")],
        default="and",
    )

    design_panels = [
        FieldPanel("favicon"),
        FieldPanel("image_password"),
        FieldPanel("image_404"),
        FieldPanel("text_404"),
    ]
    seo_panels = [
        FieldPanel("google_analytics_id"),
        FieldPanel("author"),
    ]
    social_panels = [
        MultiFieldPanel(
            [FieldPanel("linkedin_url", heading="URL")],
            heading="LinkedIn",
        ),
        MultiFieldPanel([FieldPanel("github_url", heading="URL")], heading="GitHub"),
        MultiFieldPanel(
            [FieldPanel("instagram_url", heading="URL")],
            heading="Instagram",
        ),
        MultiFieldPanel(
            [FieldPanel("facebook_url", heading="URL")],
            heading="Facebook",
        ),
        MultiFieldPanel(
            [
                FieldPanel("twitter_url", heading="URL"),
                FieldPanel("twitter_site", heading="Site", help_text="Without @"),
                FieldPanel(
                    "twitter_creator",
                    heading="Creator",
                    help_text="Without @",
                ),
            ],
            heading="Twitter",
        ),
    ]
    contact_panels = [
        FieldPanel("email"),
        FieldPanel("phone"),
    ]
    blog_panels = [
        FieldPanel("blog_pager_limit"),
    ]
    video_panels = [
        FieldPanel("video_pager_limit"),
    ]
    gallery_panels = [
        FieldPanel("gallery_collection"),
    ]
    search_panels = [
        FieldPanel("search_limit"),
        FieldPanel("search_operator"),
    ]
    cookie_panels = [
        FieldPanel("cookie_banner"),
    ]
    rss_panels = [
        FieldPanel("rss_feed"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(design_panels, heading="Design"),
            ObjectList(seo_panels, heading="SEO"),
            ObjectList(social_panels, heading="Social"),
            ObjectList(contact_panels, heading="Contact"),
            ObjectList(blog_panels, heading="Blog"),
            ObjectList(video_panels, heading="Video"),
            ObjectList(gallery_panels, heading="Gallery"),
            ObjectList(search_panels, heading="Search"),
            ObjectList(cookie_panels, heading="Cookies"),
            ObjectList(rss_panels, heading="RSS"),
        ]
    )

    class Meta:
        verbose_name = "FolioBlog"


class Menu(MultiSiteMixin, TranslatableMixin, ClusterableModel):
    name = models.CharField(max_length=255)
    homepage = models.ForeignKey(
        Page,
        on_delete=models.PROTECT,
        related_name="menu_home",
        null=True,
        blank=True,
    )
    promopage = models.ForeignKey(
        Page,
        on_delete=models.PROTECT,
        related_name="menu_promo",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    objects = I18nMultiSiteManager()

    class Meta(TranslatableMixin.Meta):
        pass

    def __str__(self):
        return self.name


class MenuLink(Orderable):
    menu = ParentalKey(Menu, related_name="links")
    related_page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="menu_link",
    )

    panels = [
        FieldPanel("related_page"),
    ]

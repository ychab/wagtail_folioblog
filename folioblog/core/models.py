import os

from django.conf import settings
from django.db import models
from django.utils.cache import add_never_cache_headers, patch_cache_control
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import (
    FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel, ObjectList,
    TabbedInterface,
)
from wagtail.contrib.settings.models import BaseGenericSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.fields import RichTextField
from wagtail.images.models import (
    AbstractImage, AbstractRendition, Image, ImageQuerySet,
)
from wagtail.models import Orderable, Page, PageManager
from wagtail.snippets.models import register_snippet

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel


class ImageManager(models.Manager):
    def get_queryset(self):
        return self._queryset_class(self.model).select_related('photographer')


@register_snippet
class Photographer(models.Model):
    name = models.CharField(max_length=255, blank=True)
    website = models.URLField(null=True, blank=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('website'),
    ]

    def __str__(self):
        return self.name


class FolioImage(AbstractImage):
    caption = models.CharField(max_length=255, blank=True)
    photographer = models.ForeignKey(Photographer, on_delete=models.SET_NULL, null=True, blank=True)

    admin_form_fields = Image.admin_form_fields + (
        'caption', 'photographer',
    )

    objects = ImageManager.from_queryset(ImageQuerySet)()

    @property
    def default_alt_text(self):
        return self.caption or self.title

    def figcaption(self, alt_text=None):
        alt_text = alt_text or self.default_alt_text

        output = f'<cite>{alt_text}</cite>'
        if self.photographer:
            output += ' - &copy; '
            if self.photographer.website:
                output += f'<a href="{self.photographer.website}" target="_blank">{self.photographer}</a>'
            else:
                output += f'{self.photographer}'

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
    image = models.ForeignKey(FolioImage, on_delete=models.CASCADE, related_name='renditions')

    class Meta:
        unique_together = (
            ('image', 'filter_spec', 'focal_point_key'),
        )

    def get_upload_to(self, filename):
        # No hash in filename? (i.e: no focal point)
        if filename.count('.') == 2:
            name, spec, ext = filename.split('.')
            filename = f'{name}.{ext}'
        else:
            # Fill images spec support focal point so they needs a hash(?)
            name, hash, *spec, ext = filename.split('.')
            spec = '.'.join(spec)
            filename = f'{name}.{hash}.{ext}'

        filename = self.file.field.storage.get_valid_name(filename)
        return os.path.join('images', slugify(self.image.collection), spec, filename)


class BaseCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BaseIndexManager(PageManager):

    def get_queryset(self):
        return self._queryset_class(self.model)\
            .select_related('image__photographer')\
            .prefetch_related('image__renditions')


class PageCacheMixin:

    def serve(self, request, *args, **kwargs):
        response = super().serve(request, *args, **kwargs)

        if request.user.is_authenticated:
            add_never_cache_headers(response)
        elif (
            request.method in ['GET', 'HEAD']
            and request.user.is_anonymous
            and response.status_code in [200, 304]
            and 'max-age' not in response.get('Cache-Control', ())
        ):
            patch_cache_control(
                response, max_age=settings.CACHE_MIDDLEWARE_SECONDS, public=True)

        return response


class BaseIndexPage(PageCacheMixin, Page):
    subheading = models.CharField(max_length=512, blank=True, default='')

    image = models.ForeignKey(
        FolioImage,
        on_delete=models.PROTECT,
        verbose_name='Image',
        related_name="%(app_label)s_%(class)s_+",
        related_query_name="%(app_label)s_%(class)ss",
    )
    image_alt = models.CharField(max_length=512, default='')

    content_panels = Page.content_panels + [
        FieldPanel('subheading'),
        MultiFieldPanel(
            [
                FieldPanel('image'),
                FieldPanel('image_alt'),
            ],
            heading=_("Image"),
        ),
    ]

    objects = BaseIndexManager()

    class Meta:
        abstract = True

    @property
    def caption(self):
        return self.image_alt or self.image.default_alt_text

    @property
    def seo_description(self):
        return self.search_description


class BasePage(BaseIndexPage):
    intro = models.TextField(default='', blank=True)
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('subheading'),
        FieldPanel('intro'),
        FieldPanel('body', classname="full"),
        MultiFieldPanel(
            [
                FieldPanel('image'),
                FieldPanel('image_alt'),
            ],
            heading=_("Image"),
        ),
    ]

    class Meta:
        abstract = True

    @property
    def seo_description(self):
        return self.intro or self.search_description


class BasicPage(BasePage):
    parent_page_types = ['portfolio.PortfolioPage']
    subpage_types = []

    content_panels = BasePage.content_panels + [
        InlinePanel('related_links', label=_('Related links')),
    ]


class BasicPageRelatedLink(Orderable):
    page = ParentalKey(BasicPage, related_name='related_links')
    related_page = ParentalKey(Page, related_name='basic_related_pages')

    panels = [
        FieldPanel('related_page'),
    ]


@register_setting(icon='cog')
class FolioBlogSettings(BaseGenericSetting):

    google_analytics_id = models.CharField(
        verbose_name=_('Google Analytics ID'),
        max_length=128,
        blank=True,
        default='',
    )

    linkedin_url = models.URLField(blank=True, default='')
    github_url = models.URLField(blank=True, default='')
    instagram_url = models.URLField(blank=True, default='')
    facebook_url = models.URLField(blank=True, default='')
    twitter_url = models.URLField(blank=True, default='')
    twitter_site = models.CharField(max_length=255, blank=True, default='')
    twitter_creator = models.CharField(max_length=255, blank=True, default='')

    email = models.EmailField(
        help_text=_('Email address used for contact form submission.'),
        blank=True,
        default='',
    )
    phone = models.CharField(max_length=128, blank=True, default='')

    cookie_banner_title = models.CharField(max_length=255, default='')
    cookie_banner_text = models.TextField()
    cookie_banner_link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='page_link',
    )
    cookie_banner_link_text = models.CharField(max_length=255, default='', blank=True,)
    cookie_banner_button_cancel_text = models.CharField(max_length=255)
    cookie_banner_button_accept_text = models.CharField(max_length=255, default='')

    rss_title = models.CharField(max_length=255, default='')
    rss_description = models.TextField(default='', blank=True)
    rss_limit = models.PositiveSmallIntegerField(default=15)

    blog_pager_limit = models.PositiveSmallIntegerField(default=8)
    video_pager_limit = models.PositiveSmallIntegerField(default=10)

    search_limit = models.PositiveSmallIntegerField(default=10)
    search_operator = models.CharField(
        max_length=3,
        choices=[('or', _('Or')), ('and', _('And'))],
        default='and',
    )

    seo_panels = [
        FieldPanel('google_analytics_id'),
    ]
    social_panels = [
        MultiFieldPanel([FieldPanel('linkedin_url', heading='URL')], heading=_('LinkedIn')),
        MultiFieldPanel([FieldPanel('github_url', heading='URL')], heading=_('GitHub')),
        MultiFieldPanel([FieldPanel('instagram_url', heading='URL')], heading=_('Instagram')),
        MultiFieldPanel([FieldPanel('facebook_url', heading='URL')], heading=_('Facebook')),
        MultiFieldPanel(
            [
                FieldPanel('twitter_url', heading='URL'),
                FieldPanel('twitter_site', heading='Site', help_text=_('Sans le @')),
                FieldPanel('twitter_creator', heading='Creator', help_text=_('Sans le @')),
            ],
            heading=_('Twitter'),
        ),
    ]
    contact_panels = [
        FieldPanel('email'),
        FieldPanel('phone'),
    ]
    blog_panels = [
        FieldPanel('blog_pager_limit'),
    ]
    video_panels = [
        FieldPanel('video_pager_limit'),
    ]
    search_panels = [
        FieldPanel('search_limit'),
        FieldPanel('search_operator'),
    ]
    cookie_panels = [
        FieldPanel('cookie_banner_title'),
        FieldPanel('cookie_banner_text'),
        FieldRowPanel(
            [
                FieldPanel('cookie_banner_link_page'),
                FieldPanel('cookie_banner_link_text'),
            ],
            heading=_("Link"),
        ),
        MultiFieldPanel(
            [
                FieldPanel('cookie_banner_button_accept_text'),
                FieldPanel('cookie_banner_button_cancel_text'),
            ],
            heading=_('Buttons'),
        ),
    ]
    rss_panels = [
        MultiFieldPanel(
            [
                FieldPanel('rss_title'),
                FieldPanel('rss_description'),
                FieldPanel('rss_limit'),
            ],
            heading=_('RSS'),
        ),
    ]

    edit_handler = TabbedInterface([
        ObjectList(seo_panels, heading=_('SEO')),
        ObjectList(social_panels, heading=_('Social')),
        ObjectList(contact_panels, heading=_('Contact')),
        ObjectList(blog_panels, heading=_('Blog')),
        ObjectList(video_panels, heading=_('Video')),
        ObjectList(search_panels, heading=_('Search')),
        ObjectList(cookie_panels, heading=_('Cookies')),
        ObjectList(rss_panels, heading=_('RSS')),
    ])

    class Meta:
        verbose_name = 'FolioBlog'


@register_snippet
class Menu(ClusterableModel):
    name = models.CharField(max_length=255)
    homepage = ParentalKey(Page, related_name='menu_home')

    panels = [
        FieldPanel('name'),
        FieldPanel('homepage'),
        InlinePanel('links', label=_('Links')),
    ]

    def __str__(self):
        return self.name


class MenuLink(Orderable):
    menu = ParentalKey(Menu, related_name='links')
    related_page = ParentalKey(Page, related_name='menu_link')

    panels = [
        FieldPanel('related_page'),
    ]

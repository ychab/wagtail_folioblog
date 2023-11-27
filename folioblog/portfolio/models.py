from django.db import models

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model
from wagtail.models import Page

from folioblog.core.managers import I18nPageManager
from folioblog.core.sitemap import SitemapPageMixin
from folioblog.portfolio.blocks import (
    ExperiencesBlock,
    ServicesBlock,
    SkillsBlock,
    TeamMembersBlock,
)

Image = get_image_model()


class PortfolioPage(SitemapPageMixin, Page):
    # Header
    header_heading = models.CharField(
        verbose_name="Title",
        max_length=128,
        default="",
    )
    header_lead = models.CharField(
        verbose_name="Slogan",
        max_length=255,
        blank=True,
        default="",
    )
    header_slide = models.ForeignKey(
        Image,
        # Should be required, ut much easier for migrations dependencies...
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Slide",
        related_name="+",
    )

    # About
    about_heading = models.CharField(
        verbose_name="Title",
        max_length=128,
        default="",
    )
    about_subheading = models.CharField(
        verbose_name="Subtitle",
        max_length=128,
        blank=True,
        default="",
    )
    about_text = RichTextField(blank=True)
    about_video = models.ForeignKey(
        "video.VideoPage",
        on_delete=models.PROTECT,
        related_name="portfolio",
        null=True,
        blank=True,
    )

    # Service
    service_subheading = models.CharField(
        verbose_name="Subtitle",
        max_length=255,
        blank=True,
        default="",
    )
    services = StreamField(
        ServicesBlock(),
        null=True,
        blank=True,
        use_json_field=True,
    )

    # Skills
    skill_subheading = models.CharField(
        verbose_name="Subtitle",
        max_length=512,
        blank=True,
        default="",
    )
    skills = StreamField(
        SkillsBlock(),
        null=True,
        blank=True,
        use_json_field=True,
    )

    # CV
    cv_heading = models.CharField(
        verbose_name="Title",
        max_length=128,
        default="",
    )
    cv_subheading = models.CharField(
        verbose_name="Subtitle",
        max_length=128,
        blank=True,
        default="",
    )
    cv_experiences = StreamField(
        ExperiencesBlock(),
        null=True,
        blank=True,
        use_json_field=True,
    )

    # Team
    team_heading = models.CharField(
        verbose_name="Title",
        max_length=128,
        default="",
    )
    team_subheading = models.CharField(
        verbose_name="Subtitle",
        max_length=128,
        blank=True,
        default="",
    )
    team_text = models.CharField(
        verbose_name="Text",
        max_length=512,
        blank=True,
        default="",
    )
    team_active = models.BooleanField(default=True)

    team_members = StreamField(
        TeamMembersBlock(),
        null=True,
        blank=True,
        use_json_field=True,
    )

    # Contact
    contact_heading = models.CharField(
        verbose_name="Title",
        max_length=128,
        default="",
    )
    contact_subheading = models.CharField(
        verbose_name="Subtitle",
        max_length=128,
        blank=True,
        default="",
    )

    objects = I18nPageManager()

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("header_lead"),
                FieldPanel("header_heading"),
                FieldPanel("header_slide"),
            ],
            heading="Header",
            classname="collapsible",
        ),
        MultiFieldPanel(
            [
                FieldPanel("about_heading"),
                FieldPanel("about_subheading"),
                FieldPanel("about_text"),
                FieldPanel("about_video"),
            ],
            heading="About",
            classname="collapsible",
        ),
        MultiFieldPanel(
            [
                FieldPanel("service_subheading"),
                FieldPanel("services"),
            ],
            heading="Services",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("skill_subheading"),
                FieldPanel("skills"),
            ],
            heading="Skills",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("cv_heading"),
                FieldPanel("cv_subheading"),
                FieldPanel("cv_experiences"),
            ],
            heading="CV",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("team_heading"),
                FieldPanel("team_subheading"),
                FieldPanel("team_text"),
                FieldPanel("team_active"),
                FieldPanel("team_members"),
            ],
            heading="Team",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("contact_heading"),
                FieldPanel("contact_subheading"),
            ],
            heading="Contact",
            classname="collapsible",
        ),
    ]

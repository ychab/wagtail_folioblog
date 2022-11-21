from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model
from wagtail.models import Page

from folioblog.portfolio.blocks import (
    ExperiencesBlock, ServicesBlock, SkillsBlock, TeamMembersBlock,
)

Image = get_image_model()


class PortfolioPage(Page):

    # Header
    header_heading = models.CharField(
        verbose_name=_('Titre'),
        max_length=128,
        default='',
    )
    header_lead = models.CharField(
        verbose_name=_('Slogan'),
        max_length=255,
        blank=True,
        default='',
    )
    header_slide = models.ForeignKey(
        Image,
        # Should be required, ut much easier for migrations dependencies...
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name=_('Slide'),
        related_name='+',
    )

    # Service
    service_subheading = models.CharField(
        verbose_name=_('Sous-titre'),
        max_length=255,
        blank=True,
        default='',
    )
    services = StreamField(
        ServicesBlock(),
        null=True,
        blank=True,
        use_json_field=True,
    )

    # Skills
    skill_subheading = models.CharField(
        verbose_name=_('Sous-titre'),
        max_length=512,
        blank=True,
        default='',
    )
    skills = StreamField(
        SkillsBlock(),
        null=True,
        blank=True,
        use_json_field=True,
    )

    # About
    about_heading = models.CharField(
        verbose_name=_('Titre'),
        max_length=128,
        default='',
    )
    about_subheading = models.CharField(
        verbose_name=_('Sous-titre'),
        max_length=128,
        blank=True,
        default='',
    )
    about_text = RichTextField(blank=True)
    about_video = models.ForeignKey(
        'video.VideoPage',
        on_delete=models.PROTECT,
        related_name='portfolio',
        null=True,
        blank=True,
    )

    # CV
    cv_heading = models.CharField(
        verbose_name=_('Titre'),
        max_length=128,
        default='',
    )
    cv_subheading = models.CharField(
        verbose_name=_('Sous-titre'),
        max_length=128,
        blank=True,
        default='',
    )
    cv_experiences = StreamField(
        ExperiencesBlock(),
        null=True,
        blank=True,
        use_json_field=True,
    )

    # Team
    team_heading = models.CharField(
        verbose_name=_('Titre'),
        max_length=128,
        default='',
    )
    team_subheading = models.CharField(
        verbose_name=_('Sous-titre'),
        max_length=128,
        blank=True,
        default='',
    )
    team_text = models.CharField(
        verbose_name=_('Texte'),
        max_length=512,
        blank=True,
        default='',
    )
    team_members = StreamField(
        TeamMembersBlock(),
        null=True,
        blank=True,
        use_json_field=True,
    )

    # Contact
    contact_heading = models.CharField(
        verbose_name=_('Titre'),
        max_length=128,
        default='',
    )
    contact_subheading = models.CharField(
        verbose_name=_('Sous-titre'),
        max_length=128,
        blank=True,
        default='',
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('header_lead'),
                FieldPanel('header_heading'),
                FieldPanel('header_slide'),
            ],
            heading=_('Entête'),
            classname="collapsible",
        ),
        MultiFieldPanel(
            [
                FieldPanel('service_subheading'),
                FieldPanel('services'),
            ],
            heading=_('Services'),
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel('skill_subheading'),
                FieldPanel('skills'),
            ],
            heading=_('Skills'),
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel('cv_heading'),
                FieldPanel('cv_subheading'),
                FieldPanel('cv_experiences'),
            ],
            heading=_('CV'),
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel('team_heading'),
                FieldPanel('team_subheading'),
                FieldPanel('team_text'),
                FieldPanel('team_members'),
            ],
            heading=_('Équipe'),
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel('about_heading'),
                FieldPanel('about_subheading'),
                FieldPanel('about_text'),
                FieldPanel('about_video'),
            ],
            heading=_('À propos'),
            classname="collapsible",
        ),
        MultiFieldPanel(
            [
                FieldPanel('contact_heading'),
                FieldPanel('contact_subheading'),
            ],
            heading=_('Contact'),
            classname="collapsible",
        ),
    ]

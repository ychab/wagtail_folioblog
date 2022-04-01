from django.utils.translation import get_language, gettext_lazy as _, to_locale

import factory
import wagtail_factories
from wagtail_factories import PageFactory

from folioblog.core.factories import ImageFactory
from folioblog.portfolio.factories.blocks import (
    ExperiencesBlockFactory, ServicesBlockFactory, SkillsBlockFactory,
    TeamMembersBlockFactory,
)
from folioblog.portfolio.models import PortfolioPage

current_locale = to_locale(get_language())


class PortfolioPageFactory(PageFactory):

    class Meta:
        model = PortfolioPage

    title = _('Portfolio')
    slug = 'portfolio'

    header_heading = factory.Faker('sentence', nb_words=3, locale=current_locale)
    header_lead = factory.Faker('sentence', nb_words=5, locale=current_locale)
    header_slide = factory.SubFactory(ImageFactory)

    service_subheading = factory.Faker('sentence', nb_words=5, locale=current_locale)
    services = wagtail_factories.StreamFieldFactory(ServicesBlockFactory)

    skill_subheading = factory.Faker('sentence', nb_words=5, locale=current_locale)
    skills = wagtail_factories.StreamFieldFactory(SkillsBlockFactory)

    about_heading = factory.Faker('sentence', nb_words=3, locale=current_locale)
    about_subheading = factory.Faker('sentence', nb_words=5, locale=current_locale)
    about_text = factory.Faker('text', locale=current_locale)
    # Parent video page is itself so it must be done at update
    # about_video = factory.SubFactory(VideoPageFactory, parent=None)

    cv_heading = factory.Faker('sentence', nb_words=3, locale=current_locale)
    cv_subheading = factory.Faker('sentence', nb_words=5, locale=current_locale)
    cv_experiences = wagtail_factories.StreamFieldFactory(ExperiencesBlockFactory)

    team_heading = factory.Faker('sentence', nb_words=3, locale=current_locale)
    team_subheading = factory.Faker('sentence', nb_words=5, locale=current_locale)
    team_text = factory.Faker('sentence', nb_words=8, locale=current_locale)
    team_members = wagtail_factories.StreamFieldFactory(TeamMembersBlockFactory)

    contact_heading = factory.Faker('sentence', nb_words=3, locale=current_locale)
    contact_subheading = factory.Faker('sentence', nb_words=5, locale=current_locale)

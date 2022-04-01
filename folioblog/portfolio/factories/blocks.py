from django.utils.translation import get_language, to_locale

from wagtail.blocks import CharBlock
from wagtail.blocks.list_block import ListBlock, ListValue
from wagtail.rich_text import RichText

import factory
import wagtail_factories
from faker import Faker

from folioblog.core.factories import ImageFactory
from folioblog.portfolio.blocks import (
    ExperienceBlock, ExperiencesBlock, ServiceBlock, ServicesBlock, SkillBlock,
    SkillLinkBlock, SkillsBlock, TeamMemberBlock, TeamMembersBlock,
)

current_locale = to_locale(get_language())
fake = Faker(locale=current_locale)


class FolioBlogImageChooserBlockFactory(wagtail_factories.ImageChooserBlockFactory):
    image = factory.SubFactory(ImageFactory)


class ServiceBlockFactory(wagtail_factories.StructBlockFactory):

    class Meta:
        model = ServiceBlock

    name = factory.Faker('sentence', nb_words=3, locale=current_locale)
    text = factory.Faker('paragraph', locale=current_locale)
    items = factory.LazyFunction(
        lambda: ListValue(ListBlock(CharBlock()), values=fake.words(nb=2)))
    # If doing this, MUST specify a value while declaring the factory (wagtail <=4.0.4)
    # items = wagtail_factories.ListBlockFactory(wagtail_factories.CharBlockFactory)
    icon = factory.Faker('word', locale=current_locale)


class ServicesBlockFactory(wagtail_factories.StreamBlockFactory):

    class Meta:
        model = ServicesBlock

    service = factory.SubFactory(ServiceBlockFactory)


class SkillLinkBlockFactory(wagtail_factories.StructBlockFactory):
    """
    @FIXME - this factory class could not be used anymore with ListBlockFactory??
    @see https://github.com/wagtail/wagtail-factories/issues/65
    """

    class Meta:
        model = SkillLinkBlock

    title = factory.Faker('sentence', nb_words=3, locale=current_locale)
    caption = factory.Faker('sentence', nb_words=5, locale=current_locale)
    page = factory.SubFactory(wagtail_factories.PageChooserBlockFactory)


class SkillBlockFactory(wagtail_factories.StructBlockFactory):

    class Meta:
        model = SkillBlock

    heading = factory.Faker('sentence', nb_words=3, locale=current_locale)
    subheading = factory.Faker('sentence', nb_words=5, locale=current_locale)
    intro = factory.Faker('sentence', nb_words=8, locale=current_locale)
    text = factory.LazyFunction(lambda: RichText(fake.text()))  # @todo use RichTextBlockFactory
    # @fixme - ListBlockFactory is not working while Wagtail 4.1 (working with 4.0.4)
    # links = wagtail_factories.ListBlockFactory(SkillLinkBlockFactory)
    links = factory.LazyFunction(
        lambda: ListValue(ListBlock(SkillLinkBlock()), values=[
            {
                'title': fake.sentence(nb_words=3),
                'caption': fake.sentence(nb_words=5),
                'page': wagtail_factories.PageChooserBlockFactory(),
            },
        ])
    )
    image = factory.SubFactory(FolioBlogImageChooserBlockFactory)


class SkillsBlockFactory(wagtail_factories.StreamBlockFactory):

    class Meta:
        model = SkillsBlock

    skill = factory.SubFactory(SkillBlockFactory)


class ExperienceBlockFactory(wagtail_factories.StructBlockFactory):

    class Meta:
        model = ExperienceBlock

    date = factory.Faker('sentence', nb_words=2, locale=current_locale)
    company = factory.Faker('company', locale=current_locale)
    text = factory.LazyFunction(lambda: RichText(fake.paragraph()))  # @todo use RichTextBlockFactory
    photo = factory.SubFactory(FolioBlogImageChooserBlockFactory)


class ExperiencesBlockFactory(wagtail_factories.StreamBlockFactory):

    class Meta:
        model = ExperiencesBlock

    experience = factory.SubFactory(ExperienceBlockFactory)


class TeamMemberBlockFactory(wagtail_factories.StructBlockFactory):

    class Meta:
        model = TeamMemberBlock

    name = factory.Faker('name', locale=current_locale)
    job = factory.Faker('job', locale=current_locale)
    photo = factory.SubFactory(FolioBlogImageChooserBlockFactory)
    photo_alt = factory.Faker('sentence', locale=current_locale)


class TeamMembersBlockFactory(wagtail_factories.StreamBlockFactory):

    class Meta:
        model = TeamMembersBlock

    member = factory.SubFactory(TeamMemberBlockFactory)

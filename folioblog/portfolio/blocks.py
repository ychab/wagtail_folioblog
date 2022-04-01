from wagtail import blocks
from wagtail.images import get_image_model
from wagtail.images.blocks import ImageChooserBlock

Image = get_image_model()


class ServiceBlock(blocks.StructBlock):
    name = blocks.CharBlock(max_length=128)
    text = blocks.TextBlock(required=False)
    items = blocks.ListBlock(
        blocks.CharBlock(
            max_length=128,
            required=False,
            icon='list-ul',
        )
    )
    icon = blocks.CharBlock(max_length=128)

    class Meta:
        template = 'portfolio/blocks/service.html'
        icon = 'cogs'


class ServicesBlock(blocks.StreamBlock):
    service = ServiceBlock()

    class Meta:
        template = 'portfolio/blocks/services.html'
        icon = 'cogs'


class SkillLinkStructValue(blocks.StructValue):

    def url(self):
        external_url = self.get('external_url')
        page = self.get('page')
        return page.url if page else external_url


class SkillLinkBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=128)
    caption = blocks.CharBlock(max_length=128, required=False)
    page = blocks.PageChooserBlock(label='Page', required=False)
    external_url = blocks.URLBlock(required=False)

    class Meta:
        icon = 'link'
        value_class = SkillLinkStructValue


class SkillBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=128)
    subheading = blocks.CharBlock(max_length=256)
    intro = blocks.CharBlock(max_length=512)
    text = blocks.RichTextBlock()
    links = blocks.ListBlock(SkillLinkBlock(), collapsed=True)
    image = ImageChooserBlock()

    class Meta:
        template = 'portfolio/blocks/skill_grid.html'
        icon = 'code'


class SkillsBlock(blocks.StreamBlock):
    skill = SkillBlock()

    class Meta:
        template = 'portfolio/blocks/skills.html'
        icon = 'code'


class ExperienceBlock(blocks.StructBlock):
    date = blocks.CharBlock(required=False)
    company = blocks.CharBlock(required=False)
    text = blocks.RichTextBlock()
    photo = ImageChooserBlock(required=False)

    class Meta:
        template = 'portfolio/blocks/experience.html'
        icon = 'date'


class ExperiencesBlock(blocks.StreamBlock):
    experience = ExperienceBlock()

    class Meta:
        template = 'portfolio/blocks/experiences.html'
        icon = 'date'


class TeamMemberBlock(blocks.StructBlock):
    name = blocks.CharBlock()
    job = blocks.CharBlock()
    photo = ImageChooserBlock()
    photo_alt = blocks.CharBlock()

    class Meta:
        template = 'portfolio/blocks/team_member.html'
        icon = 'user'


class TeamMembersBlock(blocks.StreamBlock):
    member = TeamMemberBlock()

    class Meta:
        template = 'portfolio/blocks/team.html'
        icon = 'group'

from django.conf import settings

from wagtail import blocks


class CookieBannerBlock(blocks.StructBlock):
    language = blocks.ChoiceBlock(choices=settings.LANGUAGES)

    title = blocks.CharBlock(max_length=255)
    text = blocks.TextBlock()

    page = blocks.PageChooserBlock()
    link_text = blocks.CharBlock(max_length=255, required=False)

    button_cancel_text = blocks.CharBlock(max_length=255)
    button_accept_text = blocks.CharBlock(max_length=255)


class CookieBannersBlock(blocks.StreamBlock):
    banners = CookieBannerBlock()


class RssFeedBlock(blocks.StructBlock):
    language = blocks.ChoiceBlock(choices=settings.LANGUAGES)

    title = blocks.CharBlock(max_length=255)
    description = blocks.TextBlock(required=False)
    limit = blocks.IntegerBlock(default=15)


class RssFeedsBlock(blocks.StreamBlock):
    feeds = RssFeedBlock()
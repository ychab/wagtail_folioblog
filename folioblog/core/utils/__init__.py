from django.utils.translation import get_language


def get_block_language(blocks, langcode=None):
    langcode = langcode or get_language()

    for block in blocks:
        if block.value['language'] == langcode:
            return block.value

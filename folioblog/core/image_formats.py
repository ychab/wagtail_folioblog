from django.utils.html import format_html

from wagtail.images.formats import Format, register_image_format


class CaptionedImageFormat(Format):

    def image_to_html(self, image, alt_text, extra_attributes=None):
        default_html = super().image_to_html(image, alt_text, extra_attributes)
        html = f'<figure>{default_html}<figcaption class="caption figure-caption">{alt_text}</figcaption></figure>'
        return format_html(html)


# New image format available for WISYWYG
register_image_format(
    CaptionedImageFormat(
        name='bodyfullfuild',
        label='Body Full Fluid (w940)',
        classnames='img-fluid mx-auto d-block rounded',
        filter_spec='width-940',
    )
)

from django.utils.html import format_html

from wagtail.images.formats import Format, register_image_format
from wagtail.images.shortcuts import get_rendition_or_not_found


class BodyFullImageFormat(Format):

    def image_to_html(self, image, alt_text, extra_attributes=None):
        default_html = super().image_to_html(image, alt_text, extra_attributes)
        html = f'<figure>{default_html}<figcaption class="caption figure-caption">{alt_text}</figcaption></figure>'
        return format_html(html)


class CreditLightboxImageFormat(Format):

    def image_to_html(self, image, alt_text, extra_attributes=None):
        img_html = super().image_to_html(image, alt_text, extra_attributes)
        rendition_full = get_rendition_or_not_found(image, 'width-1920|format-jpeg')
        alt_text_html = image.figcaption(alt_text)

        html = f"""
            <figure class="figure d-block">
                <a href="{rendition_full.url}"
                   class="glightbox"
                   data-glightbox="type: image; description: .custom-desc-{image.pk}; alt: {alt_text};">
                    {img_html}
                </a>
                <div class="glightbox-desc custom-desc-{image.pk}">{alt_text_html}</div>
                <figcaption class="caption figure-caption">{alt_text_html}</figcaption>
            </figure>
        """

        return format_html(html)


# New image format available for WISYWYG
register_image_format(
    BodyFullImageFormat(
        name='bodyfullfuild',
        label='Body Full (w940)',
        classnames='img-fluid mx-auto d-block rounded',
        filter_spec='width-940',
    )
)

register_image_format(
    CreditLightboxImageFormat(
        name='creditlightbox',
        label='Credit Lightbox (w940)',
        classnames='img-fluid mx-auto d-block rounded',
        filter_spec='width-940',
    )
)

from django import template

register = template.Library()

SPECS_PORTRAIT = {
    'image_xs_3x': 'fill-320x440',
    'image_xs_3x_zoom': 'fill-640x880',
    'image_lg_1x': 'fill-465x620',
    'image_lg_1x_zoom': 'fill-930x1240',
    'image_full': 'width-1920|format-jpeg',
}
SPECS_LANDSCAPE = {
    'image_xs_3x': 'fill-320x250',
    'image_xs_3x_zoom': 'fill-640x500',
    'image_lg_1x': 'fill-468x351',
    'image_lg_1x_zoom': 'fill-937x703',
    'image_full': 'width-1920|format-jpeg',
}
GALLERY_SPECS = {**SPECS_PORTRAIT, **SPECS_LANDSCAPE}


@register.inclusion_tag('gallery/gallery_grid_item.html')
def gallery_grid_item(image, extra_class=None):
    context = {
        'image': image,
        'extra_class': extra_class if image.is_landscape() else '',
    }

    if image.is_portrait():  # pragma: no cover
        specs = SPECS_PORTRAIT
    else:  # pragma: no branch
        specs = SPECS_LANDSCAPE

    renditions = {}
    for name, spec in specs.items():
        renditions[name] = image.get_rendition(spec)

    context.update(renditions)
    context['image_xs'] = context['image_xs_3x_zoom'] if context['extra_class'] else context['image_xs_3x']
    context['image_lg'] = context['image_lg_1x_zoom'] if context['extra_class'] else context['image_lg_1x']

    return context

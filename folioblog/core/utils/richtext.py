from wagtail.rich_text.rewriters import FIND_EMBED_TAG, extract_attrs


def richtext_extract_image_attrs(image_id, html):
    """
    Helper to extract embed image attribute alt from RichTextField().
    Didn't find any explicit helper for this in Wagtail source.

    @see EmbedRewriter.extract_references()
    """
    for match in FIND_EMBED_TAG.findall(html):
        attrs = extract_attrs(match)
        if attrs.get("embedtype") == "image" and attrs.get("id") == image_id:
            return attrs.get("alt")

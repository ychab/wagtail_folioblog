from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import get_language, pgettext

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.images import get_image_model
from wagtail.models import Collection, Page, ReferenceIndex, Site

from folioblog.blog.models import BlogPage
from folioblog.core.models import BaseIndexPage, BasicPage, FolioBlogSettings
from folioblog.core.utils.richtext import richtext_extract_image_attrs
from folioblog.video.models import VideoPage

Image = get_image_model()


class GalleryPage(BaseIndexPage):
    ajax_template = "gallery/gallery_page_ajax.html"

    gallery_title = models.CharField(max_length=512, blank=True, default="")
    gallery_text = RichTextField(blank=True)

    content_panels = BaseIndexPage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("gallery_title"),
                FieldPanel("gallery_text"),
            ],
            heading="Section",
        ),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        site = Site.find_for_request(request)
        site_settings = FolioBlogSettings.for_site(site)
        root_page = site.root_page.localized

        # First collect gallery collection.
        collection_qs = Collection.objects.all().order_by("name")
        if site_settings.gallery_collection:
            collection_qs = collection_qs.descendant_of(
                site_settings.gallery_collection
            )

        # Then build collection options, with ugly translation on the fly...
        collection_options = sorted(
            [
                {"name": pgettext("collection", str(c)), "value": c.pk}
                for c in collection_qs
            ],
            key=lambda x: x["name"],
        )

        # Then filter collections if any.
        collection_filter = request.GET.get("collection", None)
        if collection_filter:
            collection_subquery = collection_qs.filter(pk=collection_filter)
        else:
            collection_subquery = collection_qs.all()  # keep a copy/clone

        # Then collect images for these collections.
        image_qs = (
            Image.objects.filter(collection__in=collection_subquery)
            .select_related("collection")
            .prefetch_renditions()
            .order_by("?")
        )

        # Load image usages in bulk thanks to reference index.
        content_type_image = ContentType.objects.get_by_natural_key(
            Image._meta.app_label, Image._meta.model_name
        )
        content_type_page = ContentType.objects.get_by_natural_key(
            Page._meta.app_label, Page._meta.model_name
        )

        ref_qs = ReferenceIndex.objects.filter(
            to_content_type_id=content_type_image,
            to_object_id__in=[i.pk for i in image_qs],
            base_content_type=content_type_page,
        )

        # Preload SPECIFIC referenced pages first.
        # Because BasePage is abstract (for good reason), we cannot use it...
        pages = {}
        for SpecificPage in [BasicPage, BlogPage, VideoPage]:
            page_qs = (
                SpecificPage.objects.live()
                .select_related("image__photographer")
                .descendant_of(root_page)
                .filter(
                    locale__language_code=get_language(),
                    id__in=[int(ref.object_id) for ref in ref_qs],
                )
            )
            pages.update({p.pk: p for p in page_qs})

        # Then attach latest available pages to image with custom alt if any.
        image_refs = {}
        for ref in ref_qs:
            page = pages.get(int(ref.object_id), None)
            if page:
                if ref.model_path.startswith("body."):
                    caption = richtext_extract_image_attrs(ref.to_object_id, page.body)
                elif ref.model_path == "image":  # pragma: no branch
                    caption = page.image_alt
                else:  # pragma: no cover
                    caption = None

                image_refs[int(ref.to_object_id)] = {
                    "page": page,
                    "caption": caption,
                }

        # Then build images with attached pages.
        images = []
        for image in image_qs:
            # Ugly: add/override properties on the fly!
            image.page = image_refs.get(image.pk, {}).get("page", None)
            image.caption = image_refs.get(image.pk, {}).get("caption") or image.caption
            images.append(image)

        context.update(
            {
                "images": images,
                "collection_options": collection_options,
                "collection_filter": collection_filter,
            }
        )
        return context

from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.images import get_image_model
from wagtail.models import Collection

from folioblog.blog.models import BlogPage
from folioblog.core.models import BaseIndexPage, BasicPage
from folioblog.video.models import VideoPage

Image = get_image_model()


class GalleryPage(BaseIndexPage):
    ajax_template = 'gallery/gallery_page_ajax.html'

    gallery_title = models.CharField(max_length=512, blank=True, default='')
    gallery_text = RichTextField(blank=True)

    content_panels = BaseIndexPage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('gallery_title'),
                FieldPanel('gallery_text'),
            ],
            heading=_("Section"),
        ),
    ]

    parent_page_types = ['portfolio.PortfolioPage']
    subpage_types = []

    def serve(self, request, *args, **kwargs):
        response = super().serve(request, *args, **kwargs)
        response.headers['Link'] = f'<{self.get_full_url(request)}>; rel="canonical"'
        return response

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # First collect gallery collection.
        root_collection = Collection.objects.get(name='Gallery')
        collection_qs = Collection.objects.child_of(root_collection).order_by('name')

        # Then filter collections if any.
        collection_filter = request.GET.get('collection', None)
        if collection_filter:
            collection_subquery = collection_qs.filter(pk=collection_filter)
        else:
            collection_subquery = collection_qs.all()  # keep a copy/clone

        # Collect images for these collections.
        image_qs = Image.objects \
            .filter(collection__in=collection_subquery) \
            .select_related('collection') \
            .prefetch_renditions() \
            .order_by('?')  # just for fun, will be cached in production

        # For each images, try to attach its page if any (that's the ugly part):
        # - fetching related pages is not possible (i.e related_name='+' due to abstract)
        # - using Image.get_usage() in loop is just a performance killer
        # ... so we do it manually in that ugly way!
        # @Note: if BaseIndexPage is not abstract, we could do BaseIndexPage.objects.live()...
        image_pages = {p.image_id: p for p in BasicPage.objects.live()}  # 1 query
        image_pages.update({p.image_id: p for p in BlogPage.objects.live()})  # 2 query
        image_pages.update({p.image_id: p for p in VideoPage.objects.live()})  # never 2 without 3!

        images = []
        for image in image_qs:
            image.page = image_pages.get(image.pk, None)  # ugly properties on the fly
            images.append(image)

        context.update({
            'images': images,
            'collection_filters': [{'name': str(c), 'value': c.pk} for c in collection_qs],
            'collection_filter': collection_filter,
        })
        return context

from folioblog.core.factories import BaseIndexPageFactory
from folioblog.gallery.models import GalleryPage


class GalleryPageFactory(BaseIndexPageFactory):
    class Meta:
        model = GalleryPage

    title = "Gallery"
    slug = "gallery"

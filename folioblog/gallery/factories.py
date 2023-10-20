from django.utils.translation import gettext_lazy as _

from folioblog.core.factories import BaseIndexPageFactory
from folioblog.gallery.models import GalleryPage


class GalleryPageFactory(BaseIndexPageFactory):
    class Meta:
        model = GalleryPage

    title = _("Galerie")
    slug = "gallery"

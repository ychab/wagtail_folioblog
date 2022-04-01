from django.utils.translation import gettext_lazy as _

from folioblog.core.factories import BaseIndexPageFactory
from folioblog.home.models import HomePage


class HomePageFactory(BaseIndexPageFactory):

    class Meta:
        model = HomePage

    title = _('Accueil')
    slug = 'blog'

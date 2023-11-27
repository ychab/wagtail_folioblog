from folioblog.core.factories import BaseIndexPageFactory
from folioblog.home.models import HomePage


class HomePageFactory(BaseIndexPageFactory):
    class Meta:
        model = HomePage

    title = "Home"
    slug = "blog"

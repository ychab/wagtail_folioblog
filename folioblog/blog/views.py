from wagtail.admin.views.generic.chooser import ChooseResultsView, ChooseView
from wagtail.admin.viewsets.chooser import ChooserViewSet

from folioblog.blog.models import BlogCategory
from folioblog.core.views import MultiSiteChooseMixin


class BlogCategoryChooseView(MultiSiteChooseMixin, ChooseView):
    pass


class BlogCategoryChooseResultsView(MultiSiteChooseMixin, ChooseResultsView):
    pass


class BlogCategoryChooserViewSet(ChooserViewSet):
    model = BlogCategory

    choose_view_class = BlogCategoryChooseView
    choose_results_view_class = BlogCategoryChooseResultsView


blogcategory_chooser_viewset = BlogCategoryChooserViewSet("blogcategory_chooser")

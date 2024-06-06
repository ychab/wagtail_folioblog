from django.db.models import Prefetch

from wagtail.admin.views.generic.chooser import ChooseResultsView, ChooseView
from wagtail.admin.viewsets.chooser import ChooserViewSet

from folioblog.blog.models import BlogCategory, BlogPage, BlogPageTag
from folioblog.core.views import BasePageAPIViewSet, MultiSiteChooseMixin


class BlogPageAPIViewSet(BasePageAPIViewSet):
    model = BlogPage
    meta_fields = BasePageAPIViewSet.meta_fields + ["date", "author"]

    def get_queryset(self):
        qs = self.get_base_queryset()
        qs = qs.select_related("category", "image__photographer", "image_body__photographer")
        qs = qs.prefetch_related(
            Prefetch("tagged_items", BlogPageTag.objects.select_related("tag").all()),
        )
        return qs


class BlogCategoryChooseView(MultiSiteChooseMixin, ChooseView):
    pass


class BlogCategoryChooseResultsView(MultiSiteChooseMixin, ChooseResultsView):
    pass


class BlogCategoryChooserViewSet(ChooserViewSet):
    model = BlogCategory

    choose_view_class = BlogCategoryChooseView
    choose_results_view_class = BlogCategoryChooseResultsView


blogcategory_chooser_viewset = BlogCategoryChooserViewSet("blogcategory_chooser")

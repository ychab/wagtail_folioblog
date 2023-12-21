from django.db.models import Prefetch

from wagtail.admin.views.generic.chooser import ChooseResultsView, ChooseView
from wagtail.admin.viewsets.chooser import ChooserViewSet

from folioblog.core.views import BasePageAPIViewSet, MultiSiteChooseMixin
from folioblog.video.models import VideoCategory, VideoPage, VideoPageTag


class VideoPageAPIViewSet(BasePageAPIViewSet):
    model = VideoPage
    meta_fields = BasePageAPIViewSet.meta_fields + ["date", "author"]

    def get_queryset(self):
        qs = self.get_base_queryset()
        qs = qs.select_related(
            "category", "image__photographer", "thumbnail__photographer"
        )
        qs = qs.prefetch_related(
            Prefetch("tagged_items", VideoPageTag.objects.select_related("tag").all()),
        )
        return qs


class VideoCategoryChooseView(MultiSiteChooseMixin, ChooseView):
    pass


class VideoCategoryChooseResultsView(MultiSiteChooseMixin, ChooseResultsView):
    pass


class VideoCategoryChooserViewSet(ChooserViewSet):
    model = VideoCategory

    choose_view_class = VideoCategoryChooseView
    choose_results_view_class = VideoCategoryChooseResultsView


videocategory_chooser_viewset = VideoCategoryChooserViewSet("videocategory_chooser")

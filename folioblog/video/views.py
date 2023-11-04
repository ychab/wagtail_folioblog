from wagtail.admin.views.generic.chooser import ChooseResultsView, ChooseView
from wagtail.admin.viewsets.chooser import ChooserViewSet

from folioblog.core.views import MultiSiteChooseMixin
from folioblog.video.models import VideoCategory


class VideoCategoryChooseView(MultiSiteChooseMixin, ChooseView):
    pass


class VideoCategoryChooseResultsView(MultiSiteChooseMixin, ChooseResultsView):
    pass


class VideoCategoryChooserViewSet(ChooserViewSet):
    model = VideoCategory

    choose_view_class = VideoCategoryChooseView
    choose_results_view_class = VideoCategoryChooseResultsView


videocategory_chooser_viewset = VideoCategoryChooserViewSet("videocategory_chooser")

from wagtail import hooks
from wagtail.snippets.models import register_snippet

from folioblog.core.wagtail_hooks import (
    BaseCategorySnippetViewSet,
    BasePromoteSnippetViewSet,
    BaseTagSnippetViewSet,
)
from folioblog.video.models import VideoCategory, VideoPromote, VideoTag
from folioblog.video.views import videocategory_chooser_viewset


@hooks.register("register_admin_viewset")
def register_viewset():
    return videocategory_chooser_viewset


class VideoCategorySnippetViewSet(BaseCategorySnippetViewSet):
    model = VideoCategory


class VideoPromoteSnippetViewSet(BasePromoteSnippetViewSet):
    model = VideoPromote


class VideoTagSnippetViewSet(BaseTagSnippetViewSet):
    model = VideoTag


register_snippet(VideoCategorySnippetViewSet)
register_snippet(VideoPromoteSnippetViewSet)
register_snippet(VideoTagSnippetViewSet)

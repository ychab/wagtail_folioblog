from wagtail import hooks
from wagtail.snippets.models import register_snippet

from folioblog.blog.models import BlogCategory, BlogPromote, BlogTag
from folioblog.blog.views import blogcategory_chooser_viewset
from folioblog.core.wagtail_hooks import (
    BaseCategorySnippetViewSet,
    BasePromoteSnippetViewSet,
    BaseTagSnippetViewSet,
)


@hooks.register("register_admin_viewset")
def register_viewset():
    return blogcategory_chooser_viewset


class BlogCategorySnippetViewSet(BaseCategorySnippetViewSet):
    model = BlogCategory


class BlogPromoteSnippetViewSet(BasePromoteSnippetViewSet):
    model = BlogPromote


class BlogTagSnippetViewSet(BaseTagSnippetViewSet):
    model = BlogTag


register_snippet(BlogCategorySnippetViewSet)
register_snippet(BlogPromoteSnippetViewSet)
register_snippet(BlogTagSnippetViewSet)

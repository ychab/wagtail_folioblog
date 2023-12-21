from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from folioblog.blog.views import BlogPageAPIViewSet
from folioblog.core.sitemap import Sitemap
from folioblog.core.views import RssView
from folioblog.search import views as search_views
from folioblog.video.views import VideoPageAPIViewSet

api_router = WagtailAPIRouter("folioblogapi")
api_router.register_endpoint("posts", BlogPageAPIViewSet)
api_router.register_endpoint("videos", VideoPageAPIViewSet)

urlpatterns = [
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path(
        "sitemap.xml", sitemap, kwargs={"sitemaps": {"i18n": Sitemap}}, name="sitemap"
    ),
    path("api/v2/", api_router.urls),
]


if settings.DEBUG:  # pragma: no cover
    # Serve static and media files from development server
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if "debug_toolbar" in settings.INSTALLED_APPS:  # pragma: no cover
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]


if settings.DEBUG or settings.DEBUG_TEST:  # pragma: no branch
    # For theming/testing purpose ONLY
    from django.views.defaults import page_not_found, server_error

    urlpatterns += i18n_patterns(
        path("404/", lambda request: page_not_found(request, None), name="404"),
        path("500/", server_error, name="500"),
        prefix_default_language=False,
    )

# Turn all other patterns into i18n patterns.
urlpatterns += i18n_patterns(
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("rss.xml", RssView.as_view(), name="rss"),
    path(
        "search-autocomplete/<str:query>/",
        search_views.AutocompleteView.as_view(),
        name="search-autocomplete",
    ),
    path("", include(wagtail_urls)),
    prefix_default_language=False,
)

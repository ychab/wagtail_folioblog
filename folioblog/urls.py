from django.conf import settings
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from folioblog.core.views import RssView
from folioblog.search import views as search_views

urlpatterns = [
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    path('search-autocomplete/<str:query>/', search_views.AutocompleteView.as_view(), name='search-autocomplete'),
    path('sitemap.xml', sitemap, name='sitemap'),
    path('rss.xml', RssView.as_view(), name='rss'),
]


if settings.DEBUG:  # pragma: no cover
    # Serve static and media files from development server
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if 'debug_toolbar' in settings.INSTALLED_APPS:  # pragma: no cover
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]


if settings.DEBUG or settings.DEBUG_TEST:  # pragma: no branch
    # For theming purpose and testing
    from django.views.defaults import page_not_found, server_error
    urlpatterns += [
        path('404', lambda request: page_not_found(request, None), name='404'),
        path('500', server_error, name='500'),
    ]

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
]

from django.conf import settings

from wagtail.contrib.sitemaps.sitemap_generator import Sitemap as WagtailSitemap
from wagtail.models import Page

from folioblog.core.managers import qs_in_site_alt


class SitemapPageMixin:
    def get_sitemap_urls(self, request=None):
        ret = super().get_sitemap_urls(request=request)

        qs = self.get_translations(inclusive=True).select_related("locale")
        if len(qs) > 1:  # Have we translations?
            alternates = []

            for page in qs:
                # Add x-default only for default locale
                if page.locale.language_code == settings.LANGUAGE_CODE:
                    alternates.append(
                        {
                            "location": page.get_full_url(request),
                            "lang_code": "x-default",
                        }
                    )

                # Other alternative with explicit lang prefix in URL
                alternates.append(
                    {
                        "location": page.get_full_url(request),
                        "lang_code": page.locale.language_code,
                    }
                )

            ret[0]["alternates"] = alternates

        return ret


class Sitemap(WagtailSitemap):
    def items(self):
        qs = (
            Page.objects.live()
            .public()
            .order_by("path")
            .defer_streamfields()
            .specific()
        )
        qs = qs_in_site_alt(qs, self.get_wagtail_site())

        return qs

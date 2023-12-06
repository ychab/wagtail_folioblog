from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.utils.translation import get_language, to_locale

try:
    import factory
except ImportError:  # pragma: no cover
    is_prod = True
else:
    is_prod = False


def connect_cache_signal():
    from folioblog.core.signals import clear_cache_page

    post_save.connect(clear_cache_page, dispatch_uid="folioblog_cache_clear_save")
    post_delete.connect(clear_cache_page, dispatch_uid="folioblog_cache_clear_delete")


class CoreConfig(AppConfig):
    name = "folioblog.core"
    label = "core"
    verbose_name = "Core"

    def ready(self):
        # Connect signals only if cache page is enabled.
        if (
            "folioblog.core.middleware.AnonymousUpdateCacheMiddleware"
            in settings.MIDDLEWARE
        ):  # pragma: no cover
            connect_cache_signal()

        # Add custom faker providers per language
        if not is_prod:  # pragma: no branch
            from folioblog.core.providers import FolioBlogProvider, FolioBlogProviderFr

            current_locale = to_locale(get_language())

            providers_default = [FolioBlogProvider]
            providers_locale = {
                "fr": [FolioBlogProviderFr],
            }
            providers = providers_locale.get(current_locale, providers_default)
            for provider in providers:
                factory.Faker.add_provider(provider, locale=current_locale)

        # fmt: off
        # Load manual translations just for coverage (not needed by gettext).
        from .trans import export_trans
        export_trans()
        # fmt: on

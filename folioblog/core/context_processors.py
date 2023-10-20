from collections import OrderedDict

from django.db.models import Prefetch

from folioblog.core.models import Menu, MenuLink


def menu(request):
    context = {
        "menu_homepage": None,
        "menu_links": None,
    }

    menu = (
        Menu.objects.filter_language()
        .select_related("homepage")
        .prefetch_related(
            Prefetch(
                "links",
                queryset=MenuLink.objects.filter(related_page__live=True)
                .select_related("related_page")
                .order_by("sort_order"),
            )
        )
        .first()
    )

    if menu:
        context["menu_homepage"] = menu.homepage
        context["menu_links"] = OrderedDict(
            [(link.related_page.slug, link.related_page) for link in menu.links.all()]
        )

    return context

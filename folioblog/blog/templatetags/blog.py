from django import template

register = template.Library()


@register.inclusion_tag("blog/snippets/blog_promoted.html", takes_context=True)
def blog_promoted(context, snippet):
    return {
        "snippet": snippet,
        "menu_links": context["menu_links"],
    }


@register.inclusion_tag("blog/image_switch.html")
def image_switch(page):
    return {
        "page": page,
        "has_switch": bool(page.image_body),
    }

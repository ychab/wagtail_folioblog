from django.template.defaulttags import register
from django.utils.translation import get_language


@register.inclusion_tag("video/youtube_player.html")
def youtube_player(page):
    return {
        "page": page,
        "lang": get_language(),
    }


@register.inclusion_tag("video/snippets/video_promoted.html", takes_context=True)
def video_promoted(context, snippet):
    return {
        "snippet": snippet,
        "menu_links": context["menu_links"],
    }

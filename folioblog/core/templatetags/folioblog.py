import base64 as base64py
import mimetypes
from urllib.parse import parse_qs, urlencode

from django import template
from django.utils.encoding import force_bytes
from django.utils.translation import get_language

from wagtail.images import get_image_model
from wagtail.models import Page, Site

from django_social_share.templatetags.social_share import (
    post_to_facebook,
    post_to_reddit,
    post_to_twitter,
)
from django_social_share.templatetags.social_share import urlencode as tpl_urlencode

from folioblog.core.models import Photographer
from folioblog.core.utils import get_block_language

register = template.Library()
Image = get_image_model()


@register.filter(is_safe=True)
def base64(value):
    # @see django.utils.http.urlsafe_base64_encode
    return base64py.b64encode(force_bytes(value)).rstrip(b"\n=").decode("ascii")


@register.filter
def mimetype(url):
    return mimetypes.guess_type(url)[0]


@register.filter
def page_translations(page, inclusive=True):
    return page.get_translations(inclusive=inclusive).live()


@register.simple_tag(takes_context=True)
def query_string(context, key, value):
    parts = parse_qs(context["request"].META.get("QUERY_STRING", ""))
    parts[key] = [value]
    return urlencode(parts, doseq=True)


@register.simple_tag
def figcaption(image_or_page):
    page = image_or_page if isinstance(image_or_page, Page) else None
    image = page.image if page else image_or_page
    return image.figcaption(page.caption if page else image.default_alt_text)


@register.simple_tag(takes_context=True)
def text_404(context, field, default=""):
    langcode = context["LANGUAGE_CODE"]
    site_settings = context["settings"]["core"]["folioblogsettings"]

    texts = get_block_language(site_settings.text_404, langcode) or {}
    return texts.get(field, default)


@register.inclusion_tag("core/cookies_banner.html", takes_context=True)
def cookies_banner(context):
    langcode = context["LANGUAGE_CODE"]
    banner_settings = get_block_language(
        context["settings"]["core"]["folioblogsettings"].cookie_banner, langcode
    )
    return {
        "settings": banner_settings,
    }


@register.inclusion_tag("core/background.html")
def background_style(image, xs_3x_spec="fill-1080x1380", lg_1x_spec="fill-1905x560"):
    return {
        "bg_xs_3x": image.get_rendition(xs_3x_spec),
        "bg_lg_1x": image.get_rendition(lg_1x_spec),
    }


@register.inclusion_tag("core/credits.html", takes_context=True)
def photo_credits(context):
    return {
        "photographers": Photographer.objects.in_site(context["current_site"]),
    }


@register.inclusion_tag("core/filter_dropdown.html")
def filter_dropdown(wrapper_id, filter_name, title, page, filter_query, filters):
    return {
        "wrapper_id": wrapper_id,
        "filter_name": filter_name,
        "title": title,
        "page": page,
        "filter_query": filter_query,
        "filters": filters,
    }


@register.inclusion_tag("core/social_links.html", takes_context=True)
def social_links(context, page):
    extra_context = {}

    page_full_url = page.get_full_url(request=context["request"])

    extra_context["reddit_url"] = post_to_reddit(context, page.title, page_full_url)[
        "reddit_url"
    ]
    extra_context["facebook_url"] = post_to_facebook(context, page_full_url)[
        "facebook_url"
    ]
    extra_context["twitter_url"] = post_to_twitter(context, page.title, page_full_url)[
        "tweet_url"
    ]
    # Don't want ugly JS plugin which write cookies and force layout button!
    # Old way, but still working?? Because new (offline) doesn't seems to work...
    # @see https://stackoverflow.com/questions/33426752/linkedin-share-post-url
    extra_context[
        "linkedin_url"
    ] = f"https://www.linkedin.com/shareArticle?url={tpl_urlencode(page_full_url)}"

    return extra_context


@register.inclusion_tag("core/og_meta.html", takes_context=True)
def og_meta(context, page, image=None, embed=None):
    og_types = {
        "blog.BlogPage": "article",
        "video.VideoPage": "video.other",
    }
    image = image or page.image
    return {
        "page": page,
        "image": image,
        "image_alt": getattr(page, "caption", None) or image.default_alt_text,
        "embed": embed or getattr(page, "embed", None),
        "og_type": og_types.get(page._meta.label, "website"),
        "site": Site.find_for_request(request=context.get("request")),
        "seo_description": getattr(page, "seo_description", None)
        or page.search_description,
    }


@register.inclusion_tag("core/twitter_card.html", takes_context=True)
def twitter_card(context, page, embed=None):
    card_types = {
        "blog.BlogPage": "summary_large_image",
        "video.VideoPage": "player",
    }
    return {
        "card": card_types.get(page._meta.label, "summary"),
        "embed": embed or getattr(page, "embed", None),
        "fb_settings": context["settings"]["core"]["FolioBlogSettings"],
    }


@register.inclusion_tag("core/related_page.html")
def related_page(page):
    return {
        # Don't trust deprecated Meta.ordering in Orderable model base.
        "related_links": page.related_links.filter(
            related_page__live=True, related_page__locale__language_code=get_language()
        ).order_by("sort_order"),
    }


@register.inclusion_tag("core/language_selector.html")
def language_selector(page):
    return {
        "translations": page.get_translations().live(),
    }

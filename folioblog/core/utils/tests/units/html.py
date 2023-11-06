from html import unescape

from bs4 import BeautifulSoup


class BaseIndexHTMLPage:
    og_properties = [
        "og:type",
        "og:site_name",
        "og:locale",
        "og:title",
        "og:url",
        "og:description",
        "og:image",
        "og:image:type",
        "og:image:width",
        "og:image:height",
        "og:image:alt",
    ]
    twitter_properties = [
        "twitter:card",
    ]

    def __init__(self, response):
        html = unescape(response.content.decode())
        self.soup = BeautifulSoup(html, features="html.parser")
        self.response = response

    def get_title(self):
        return self.soup.title.text

    def get_status_code(self):
        return self.response.status_code

    def get_masterhead_content(self):
        return self.soup.find(class_="masthead").text

    def get_meta_og(self):
        props = {}
        for og_prop in self.og_properties:
            prop_elem = self.soup.find(name="meta", property=og_prop)
            props[og_prop] = prop_elem.get("content")
        return props

    def get_meta_twitter(self):
        props = {}
        for meta_prop in self.twitter_properties:
            prop_elem = self.soup.find(name="meta", attrs={"name": meta_prop})
            props[meta_prop] = prop_elem.get("content")

        return props

    def get_canonical_href(self):
        return self.soup.find(name="link", attrs={"rel": "canonical"}).attrs["href"]

    def get_meta_lang(self):
        return self.soup.html["lang"]

    def get_meta_alternates(self):
        return [
            elem.attrs["href"]
            for elem in self.soup.find_all(name="link", attrs={"rel": "alternate"})
            if elem.attrs.get("hreflang")
        ]

    def get_filter_categories(self):
        filters = {}

        elems = self.soup.find(id="filters-dropdown").find_all("a")
        for elem in elems:
            slug = elem.get("data-filter").replace("category-", "")
            if slug == "*":
                continue
            filters[slug] = elem

        return filters


class BaseHTMLPage(BaseIndexHTMLPage):
    def get_intro(self):
        return self.soup.find(class_="page-intro").text

    def get_body(self):
        return self.soup.find(class_="page-body-text").text

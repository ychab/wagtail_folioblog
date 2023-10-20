from folioblog.core.utils.tests.units import BaseHTMLPage


class BlogPostHTMLPage(BaseHTMLPage):
    og_properties = BaseHTMLPage.og_properties + [
        "article:published_time",
        "article:modified_time",
        "article:section",
        "article:tag",  # multiple, special handling
    ]

    def get_meta_og(self):
        props = super().get_meta_og()

        elems = self.soup.find_all(name="meta", property="article:tag")
        props["article:tag"] = [elem.get("content") for elem in elems]

        return props

    def get_social_links(self):
        return self.soup.find(class_="social-links")

    def get_blockquote_with_caption(self):
        elem = self.soup.find(class_="post-blockquote")
        return {
            "blockquote": elem.find(name="blockquote").text,
            "caption": elem.find(name="figcaption").text,
        }

    def get_related_pages(self):
        data = []

        elems = self.soup.find_all(class_="related-page")
        for elem in elems:
            data.append(
                {
                    "title": elem.find(class_="related-page-title").text,
                    "url": elem.find(class_="related-page-link").get("href"),
                }
            )

        return data

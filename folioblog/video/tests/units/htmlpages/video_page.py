from folioblog.core.utils.tests.units import BaseHTMLPage


class VideoHTMLPage(BaseHTMLPage):

    og_properties = BaseHTMLPage.og_properties + [
        'og:video',
        'og:video:type',
        'og:video:width',
        'og:video:height',
        'video:release_date',
        'video:tag',  # multiple, special handling
    ]

    twitter_properties = BaseHTMLPage.twitter_properties + [
        'twitter:player',
        'twitter:player:width',
        'twitter:player:height',
    ]

    def get_meta_og(self):
        props = super().get_meta_og()

        elems = self.soup.find_all(name='meta', property='video:tag')
        props['video:tag'] = [elem.get('content') for elem in elems]

        return props

    def get_social_links(self):
        return self.soup.find(class_='social-links')

from folioblog.core.utils.tests.units import BaseIndexHTMLPage


class PortFolioHTMLPage(BaseIndexHTMLPage):

    og_properties = BaseIndexHTMLPage.og_properties + [
        'og:video',
        'og:video:type',
        'og:video:width',
        'og:video:height',
    ]

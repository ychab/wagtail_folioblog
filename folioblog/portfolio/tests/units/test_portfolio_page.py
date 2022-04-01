from html import unescape

from django.test import TestCase

from wagtail.models import Site

from folioblog.core.templatetags.folioblog import mimetype
from folioblog.home.factories import HomePageFactory
from folioblog.portfolio.factories import PortfolioPageFactory
from folioblog.portfolio.tests.units.htmlpages import PortFolioHTMLPage
from folioblog.video.factories import VideoIndexPageFactory, VideoPageFactory


class PortfolioPageTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Due to PortfolioPage which doesn't seems to support deepcopy(), we
        cannot use setUpTestData(). However, we could still inject data (shared)
        between testmethods just after the SQL transaction begin!
        """
        super().setUpClass()

        cls.site = Site.objects.get(is_default_site=True)
        cls.root_page_original = cls.site.root_page

        cls.page = PortfolioPageFactory(
            parent=None,
            services__0='service',
            skills__0='skill',
            cv_experiences__0='experience',
            team_members__0='member',
        )
        cls.site.root_page = cls.page
        cls.site.save()

        cls.index_blog = HomePageFactory(parent=cls.page)
        cls.index_video = VideoIndexPageFactory(parent=cls.page)
        cls.video_page = VideoPageFactory(parent=cls.index_video)

        cls.page.about_video = cls.video_page
        cls.page.save(update_fields=['about_video'])

    @classmethod
    def tearDownClass(cls):
        # Because we change the site root page which is created by migrations,
        # it would affect next TestCases even if rollback is done because the
        # root page was done BEFORE entering into the SQL transaction.
        # As a result, we need to reset it manually.
        cls.site.root_page = cls.root_page_original
        cls.site.save(update_fields=['root_page'])
        super().tearDownClass()

    def test_block_services(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn(self.page.services[0].value['name'], html)
        self.assertIn(self.page.services[0].value['text'], html)
        self.assertIn(self.page.services[0].value['icon'], html)
        self.assertIn(self.page.services[0].value['items'][0], html)
        self.assertIn(self.page.services[0].value['items'][1], html)

    def test_block_skills(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn(self.page.skills[0].value['heading'], html)
        self.assertIn(self.page.skills[0].value['subheading'], html)
        self.assertIn(self.page.skills[0].value['intro'], html)
        self.assertIn(str(self.page.skills[0].value['text']), html)
        self.assertIn(self.page.skills[0].value['links'][0]['title'], html)
        self.assertIn(self.page.skills[0].value['links'][0]['caption'], html)
        self.assertIn(self.page.skills[0].value['links'][0]['page'].url, html)
        self.assertIn(self.page.skills[0].value['image'].default_alt_text, html)

    def test_block_experiences(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn(self.page.cv_experiences[0].value['date'], html)
        self.assertIn(self.page.cv_experiences[0].value['company'], html)
        self.assertIn(str(self.page.cv_experiences[0].value['text']), html)
        self.assertIn(self.page.cv_experiences[0].value['photo'].default_alt_text, html)

    def test_block_team_members(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn(self.page.team_members[0].value['name'], html)
        self.assertIn(self.page.team_members[0].value['job'], html)
        self.assertIn(self.page.team_members[0].value['photo_alt'], html)

    def test_video(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn('video-youtube-thumbnail', html)
        self.assertIn(self.page.about_video.thumbnail.default_alt_text, html)
        self.assertIn(self.page.about_video.thumbnail.filename.split('.')[0], html)


class PortFolioHTMLTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        site = Site.objects.get(is_default_site=True)

        HomePageFactory()  # Just for link in menu
        video_page = VideoPageFactory(parent=site.root_page)

        cls.page = PortfolioPageFactory(
            parent=site.root_page,
            services__0='service',
            services__1='service',
            services__2='service',
            skills__0='skill',
            skills__1='skill',
            skills__2='skill',
            cv_experiences__0='experience',
            cv_experiences__1='experience',
            cv_experiences__2='experience',
            team_members__0='member',
            team_members__1='member',
            team_members__2='member',
            # The video to click on
            about_video=video_page,
        )

    def setUp(self):
        response = self.client.get(self.page.url)
        self.htmlpage = PortFolioHTMLPage(response)

    def test_title(self):
        self.assertEqual(self.htmlpage.get_title(), self.page.title)

    def test_masthead_content(self):
        masthead_txt = self.htmlpage.get_masterhead_content().replace('\n', '')
        self.assertIn(self.page.header_lead, masthead_txt)
        self.assertIn(self.page.header_heading, masthead_txt)

    def test_meta_og(self):
        meta = self.htmlpage.get_meta_og()
        embed = self.page.about_video.embed
        rendition = self.page.header_slide.get_rendition('fill-2400x1260|format-jpeg')

        self.assertEqual(meta['og:type'], 'website')
        self.assertEqual(meta['og:site_name'], self.page.get_site().site_name)
        self.assertEqual(meta['og:locale'], self.page.locale.language_code)
        self.assertEqual(meta['og:title'], self.page.title)
        self.assertEqual(meta['og:url'], self.page.full_url)
        self.assertEqual(meta['og:description'], self.page.search_description)
        self.assertEqual(meta['og:image'], rendition.full_url)
        self.assertEqual(meta['og:image:type'], mimetype(rendition.url))
        self.assertEqual(int(meta['og:image:width']), rendition.width)
        self.assertEqual(int(meta['og:image:height']), rendition.height)
        self.assertEqual(meta['og:image:alt'], rendition.alt)

        self.assertEqual(meta['og:video'], embed.url)
        self.assertEqual(meta['og:video:type'], 'text/html')
        self.assertEqual(int(meta['og:video:width']), embed.width)
        self.assertEqual(int(meta['og:video:height']), embed.height)

    def test_meta_twitter(self):
        meta = self.htmlpage.get_meta_twitter()
        self.assertEqual(meta['twitter:card'], 'summary')

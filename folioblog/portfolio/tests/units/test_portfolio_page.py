from html import unescape

from django.conf import settings
from django.test import TestCase

from wagtail.models import Site

from wagtail_factories import PageFactory

from folioblog.core.factories import LocaleFactory
from folioblog.core.templatetags.folioblog import mimetype
from folioblog.home.factories import HomePageFactory
from folioblog.portfolio.factories import PortfolioPageFactory
from folioblog.portfolio.tests.units.htmlpages import PortFolioHTMLPage
from folioblog.video.factories import VideoIndexPageFactory, VideoPageFactory


class PortfolioPageTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)

        cls.page = PortfolioPageFactory(
            parent=cls.site.root_page,
            services__0="service",
            skills__0__skill__links__0__page=PageFactory(parent=cls.site.root_page),
            cv_experiences__0="experience",
            team_members__0="member",
        )

        cls.index_blog = HomePageFactory(parent=cls.page)
        cls.index_video = VideoIndexPageFactory(parent=cls.page)
        cls.video_page = VideoPageFactory(parent=cls.index_video)

        cls.page.about_video = cls.video_page
        cls.page.save(update_fields=["about_video"])

    def test_block_services(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn(self.page.services[0].value["name"], html)
        self.assertIn(self.page.services[0].value["text"], html)
        self.assertIn(self.page.services[0].value["icon"], html)
        self.assertIn(self.page.services[0].value["items"][0], html)
        self.assertIn(self.page.services[0].value["items"][1], html)

    def test_block_skills(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn(self.page.skills[0].value["heading"], html)
        self.assertIn(self.page.skills[0].value["subheading"], html)
        self.assertIn(self.page.skills[0].value["intro"], html)
        self.assertIn(str(self.page.skills[0].value["text"]), html)
        self.assertIn(self.page.skills[0].value["links"][0]["title"], html)
        self.assertIn(self.page.skills[0].value["links"][0]["caption"], html)
        self.assertIn(self.page.skills[0].value["links"][0]["page"].url, html)
        self.assertIn(self.page.skills[0].value["image"].default_alt_text, html)

    def test_block_experiences(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn(self.page.cv_experiences[0].value["date"], html)
        self.assertIn(self.page.cv_experiences[0].value["company"], html)
        self.assertIn(str(self.page.cv_experiences[0].value["text"]), html)
        self.assertIn(self.page.cv_experiences[0].value["photo"].default_alt_text, html)

    def test_block_team_members(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn(self.page.team_members[0].value["name"], html)
        self.assertIn(self.page.team_members[0].value["job"], html)
        self.assertIn(self.page.team_members[0].value["photo_alt"], html)

    def test_video(self):
        response = self.client.get(self.page.url)
        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())

        self.assertIn("video-youtube-thumbnail", html)
        self.assertIn(self.page.about_video.thumbnail.default_alt_text, html)
        self.assertIn(self.page.about_video.thumbnail.filename.split(".")[0], html)


class PortFolioHTMLTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)

        video_page = VideoPageFactory(parent=site.root_page)

        cls.page = PortfolioPageFactory(
            parent=site.root_page,
            services__0="service",
            services__1="service",
            services__2="service",
            skills__0="skill",
            skills__1="skill",
            skills__2="skill",
            cv_experiences__0="experience",
            cv_experiences__1="experience",
            cv_experiences__2="experience",
            team_members__0="member",
            team_members__1="member",
            team_members__2="member",
            # The video to click on
            about_video=video_page,
        )

    def setUp(self):
        response = self.client.get(self.page.url)
        self.htmlpage = PortFolioHTMLPage(response)

    def test_title(self):
        self.assertEqual(self.htmlpage.get_title(), self.page.title)

    def test_masthead_content(self):
        masthead_txt = self.htmlpage.get_masterhead_content().replace("\n", "")
        self.assertIn(self.page.header_lead, masthead_txt)
        self.assertIn(self.page.header_heading, masthead_txt)

    def test_meta_og(self):
        meta = self.htmlpage.get_meta_og()
        embed = self.page.about_video.embed
        rendition = self.page.header_slide.get_rendition("fill-2400x1260|format-jpeg")

        self.assertEqual(meta["og:type"], "website")
        self.assertEqual(meta["og:site_name"], self.page.get_site().site_name)
        self.assertEqual(meta["og:locale"], self.page.locale.language_code)
        self.assertEqual(meta["og:title"], self.page.title)
        self.assertEqual(meta["og:url"], self.page.full_url)
        self.assertEqual(meta["og:description"], self.page.search_description)
        self.assertEqual(meta["og:image"], rendition.full_url)
        self.assertEqual(meta["og:image:type"], mimetype(rendition.url))
        self.assertEqual(int(meta["og:image:width"]), rendition.width)
        self.assertEqual(int(meta["og:image:height"]), rendition.height)
        self.assertEqual(meta["og:image:alt"], rendition.alt)

        self.assertEqual(meta["og:video"], embed.url)
        self.assertEqual(meta["og:video:type"], "text/html")
        self.assertEqual(int(meta["og:video:width"]), embed.width)
        self.assertEqual(int(meta["og:video:height"]), embed.height)

    def test_meta_twitter(self):
        meta = self.htmlpage.get_meta_twitter()
        self.assertEqual(meta["twitter:card"], "summary")

    def test_meta_canonical(self):
        href = self.htmlpage.get_canonical_href()
        self.assertEqual(href, self.page.full_url)


class HomeHTMLi18nTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)

        locale_fr = LocaleFactory(language_code="fr")
        locale_en = LocaleFactory(language_code="en")

        # First create required links and their translations
        homepage_fr = HomePageFactory(parent=site.root_page, locale=locale_fr)
        homepage_fr.copy_for_translation(
            locale=locale_en,
            copy_parents=True,
            alias=True,
        )
        video_fr = VideoPageFactory(parent=site.root_page, locale=locale_fr)
        video_en = video_fr.copy_for_translation(
            locale=locale_en,
            copy_parents=True,
            alias=True,
        )

        # Then create portfolio pages
        cls.page_fr = PortfolioPageFactory(
            parent=site.root_page,
            locale=locale_fr,
            about_video=video_fr,
        )
        cls.page_en = cls.page_fr.copy_for_translation(
            locale=locale_en,
            copy_parents=True,
            alias=True,
        )
        cls.page_en.about_video = video_en
        cls.page_en.save()

    def test_lang_default(self):
        response = self.client.get(self.page_fr.url)
        htmlpage = PortFolioHTMLPage(response)
        self.assertEqual(htmlpage.get_meta_lang(), settings.LANGUAGE_CODE)

    def test_lang_fr(self):
        response = self.client.get(self.page_fr.url)
        htmlpage = PortFolioHTMLPage(response)
        self.assertEqual(htmlpage.get_meta_lang(), self.page_fr.locale.language_code)

    def test_lang_en(self):
        response = self.client.get(self.page_en.url)
        htmlpage = PortFolioHTMLPage(response)
        self.assertEqual(htmlpage.get_meta_lang(), self.page_en.locale.language_code)

    def test_alternates(self):
        response = self.client.get(self.page_fr.url)
        htmlpage = PortFolioHTMLPage(response)

        self.assertListEqual(
            sorted(htmlpage.get_meta_alternates()),
            sorted([page.full_url for page in [self.page_fr, self.page_en]]),
        )

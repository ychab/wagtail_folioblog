import logging
import os
from html import unescape

from django.test import TestCase
from django.urls import reverse

from wagtail.models import Site

from bs4 import BeautifulSoup

from folioblog.user.factories import UserFactory
from folioblog.video.factories import VideoPageFactory


class EmbedAdminViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)

        cls.user = UserFactory(is_superuser=True, is_staff=True)
        cls.url = reverse('wagtailembeds_embed_modeladmin_index')
        cls.video_page = VideoPageFactory(parent=site.root_page)

    def test_url_link(self):
        self.client.force_login(self.user)

        # Turn off logging due to django.template errors with wagtail!
        logging.disable(logging.DEBUG)
        response = self.client.get(self.url)
        logging.disable(logging.NOTSET)

        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())
        soup = BeautifulSoup(html, features='html.parser')
        link = soup.find(href=self.video_page.embed.url)
        self.assertEqual(link.text, self.video_page.embed.url)

    def test_thumbnail_link(self):
        self.client.force_login(self.user)

        # Turn off logging due to django.template errors with wagtail!
        logging.disable(logging.DEBUG)
        response = self.client.get(self.url)
        logging.disable(logging.NOTSET)

        self.assertEqual(response.status_code, 200)
        html = unescape(response.content.decode())
        soup = BeautifulSoup(html, features='html.parser')
        thumbnail_url = self.video_page.embed.thumbnail_url
        link = soup.find(href=thumbnail_url)
        self.assertEqual(link.text, os.path.basename(thumbnail_url))

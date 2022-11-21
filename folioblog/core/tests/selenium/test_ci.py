from selenium.webdriver.common.by import By

from folioblog.blog.factories import (
    BlogCategoryFactory, BlogIndexPageFactory, BlogPageFactory,
)
from folioblog.blog.tests.selenium.webpages import BlogIndexWebPage
from folioblog.core.utils.tests import FolioBlogSeleniumServerTestCase

# class BasicPageTestCI(FolioBlogSeleniumServerTestCase):
#
#     has_mobile = False  # Test without for now
#
#     def setUp(self):
#         super().setUp()
#         self.page = BasicPageFactory(parent=self.site.root_page)
#         self.webpage = BasicWebPage(self.selenium)
#
#     def test_fetch_and_click_banner(self):
#         self.webpage.cookie_consent_reset()
#         self.webpage.fetch_page(self.page.full_url, force_consent=False)
#
#         button = self.selenium.find_element(By.ID, 'cookies-eu-accept')
#         button.click()
#
#         return WebDriverWait(self.selenium, 5).until(
#             EC.invisibility_of_element_located((By.ID, "cookies-eu-banner")),
#         )


class BlogIndexPageTestCI(FolioBlogSeleniumServerTestCase):

    has_mobile = False  # Test without for now

    def setUp(self):
        super().setUp()

        self.categories = [
            BlogCategoryFactory(name='tech'),
            BlogCategoryFactory(name='economie'),
            BlogCategoryFactory(name='philosophie'),
        ]

        self.page = BlogIndexPageFactory(parent=self.site.root_page)
        self.posts = [
            BlogPageFactory(
                parent=self.page,
                category=self.categories[0],
            ),
            BlogPageFactory(
                parent=self.page,
                category=self.categories[0],
            ),
            BlogPageFactory(
                parent=self.page,
                category=self.categories[2],
            ),
        ]

        self.webpage = BlogIndexWebPage(self.selenium)
        self.webpage.fetch_page(self.page.full_url)

    def test_filter_click(self):
        button = self.selenium.find_element(By.ID, 'dropdownFilter')
        button.click()

from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import all_of
from selenium.webdriver.support.wait import WebDriverWait

from folioblog.core.utils.tests.selenium import BaseIndexWebPage
from folioblog.home.tests.selenium.conditions import (
    player_link_match, player_thumbnail_match,
)


class HomeWebPage(BaseIndexWebPage):

    def scroll_to_carousel_post(self):
        return self.scroll_to((By.CLASS_NAME, 'carousel-posts'))

    def promoted_posts_next(self):
        elems = self.selenium.find_elements(By.CSS_SELECTOR, '.carousel-posts .carousel-cell')
        next = self.selenium.find_element(By.CSS_SELECTOR, '.carousel-posts .next')
        for i in range(1, len(elems)):
            next.click()

            WebDriverWait(self.selenium, 5).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, '.carousel-posts .flickity-page-dots button.is-selected'),
                    f'View slide {i + 1}',
                )
            )

    def promoted_posts_dragdrop(self):
        elems = self.selenium.find_elements(By.CSS_SELECTOR, '.carousel-posts .carousel-cell')
        for i, elem in enumerate(elems[1:]):
            ActionChains(self.selenium) \
                .drag_and_drop(elem, elems[i - 1])\
                .perform()

            WebDriverWait(self.selenium, 5).until(
                EC.text_to_be_present_in_element(
                    (By.CSS_SELECTOR, '.carousel-posts .flickity-page-dots button.is-selected'),
                    f'View slide {i + 2}',
                )
            )

    def is_last_slide(self, last_index):
        page_dot = self.selenium.find_element(
            By.CSS_SELECTOR,
            '.carousel-posts .flickity-page-dots button.is-selected',
        )
        return page_dot.text == f'View slide {last_index}'

    def scroll_to_carousel_videos(self):
        return self.scroll_to((By.CLASS_NAME, 'carousel-videos'))

    def click_video_thumbnail(self, index):
        elem = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                f'.carousel-videos .carousel-cell:nth-child({index}) .carousel-video-item',
            )),
        )
        elem.click()
        return elem

    def select_video(self, index, is_mobile):
        elem = self.click_video_thumbnail(index)
        expected_link = elem.get_attribute('data-page-url')
        expected_src = elem.get_attribute('data-img-xs-url' if is_mobile else 'data-img-lg-url')

        return WebDriverWait(self.selenium, 2).until(
            all_of(
                player_link_match(expected_link),
                player_thumbnail_match(expected_src),
            )
        )

    def play_video_of(self, index):
        elem = self.click_video_thumbnail(index)
        video_id = elem.get_attribute('data-video-id')
        expected_link = elem.get_attribute('data-page-url')

        # First wait for thumbnail to disappear.
        is_triggered = WebDriverWait(self.selenium, 2).until(
            player_link_match(expected_link))

        # Then wait for YouTube to insert the iframe.
        try:
            is_loaded = WebDriverWait(self.selenium, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe#youtube-video-{video_id}')))
        except TimeoutException:  # pragma: no cover
            # Because YouTube maybe very slow, we won't wait indefinitely...
            is_loaded = False

        return is_triggered, is_loaded

from selenium.webdriver.common.by import By

from folioblog.core.utils.selenium import BaseIndexWebPage


class VideoIndexWebPage(BaseIndexWebPage):

    def scroll_down(self, expected_count):
        return super().scroll_down(
            (By.CSS_SELECTOR, '.video-item'),
            expected_count,
        )

    def scroll_to_video(self, index):
        locator = (By.CSS_SELECTOR, f'.video-item:nth-child({index}) .video-youtube-thumbnail')
        return super().scroll_to_video(locator)

    def filter_category(self, slug, expected_count):
        return super().filter_category(
            (By.ID, 'video-filter-category'),
            (By.CLASS_NAME, 'video-item'),
            slug,
            expected_count,
        )

    def play_video(self, index):
        locator = (By.CSS_SELECTOR, f'.video-item:nth-child({index}) .youtube-player-button')
        return super().play_video(locator)

    def stop_video(self, index):
        locator = (By.CSS_SELECTOR, f'.video-item:nth-child({index}) .video-youtube-player-wrapper')
        return super().stop_video(locator)

    def get_grid_items(self):
        items = []

        elems = self.selenium.find_elements(By.CLASS_NAME, 'video-item')
        for elem in elems:
            items.append({
                'elem': elem,
                'title': elem.find_element(By.CLASS_NAME, 'video-title').text,
                'subtitle': elem.find_element(By.CLASS_NAME, 'video-subtitle').text,
                'link': elem.find_element(By.CLASS_NAME, 'video-link').get_attribute('href'),
                'category': elem.find_element(By.CLASS_NAME, 'video-category').text,
                'intro': elem.find_element(By.CLASS_NAME, 'video-intro').text,
                'img_src': elem.find_element(By.TAG_NAME, 'img').get_property('currentSrc'),
                'tags': elem.find_element(By.CLASS_NAME, 'video-tags').text,
            })

        return items

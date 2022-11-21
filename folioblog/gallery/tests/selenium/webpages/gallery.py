from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from folioblog.core.utils.tests.selenium import (
    BaseIndexWebPage, has_count_expected, has_css_class,
)
from folioblog.gallery.tests.selenium.conditions import is_checked


class GalleryWebPage(BaseIndexWebPage):

    def filter_collection(self, collection_pk, expected_count):
        elem = WebDriverWait(self.selenium, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#gallery-filters button'))
        )
        elem.click()  # Click on button to display filter list

        elem = WebDriverWait(self.selenium, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, f'a[data-filter="collection-{collection_pk}"]'))
        )
        elem.click()  # Then click on filter!

        return WebDriverWait(self.selenium, 5).until(
            EC.all_of(
                EC.invisibility_of_element_located((By.ID, 'filters-dropdown')),
                has_count_expected((By.CLASS_NAME, 'grid-item'), expected_count),
            )

        )

    def scroll_to_check(self):
        return self.scroll_to((By.ID, 'button-shuffle'))

    def check(self):
        elems = self.selenium.find_elements(By.CSS_SELECTOR, '.grid-item img')
        positions = [elem.rect for elem in elems]

        button = self.selenium.find_element(By.ID, 'button-shuffle')
        button.click()

        return WebDriverWait(self.selenium, 5).until(
            is_checked(positions),
        )

    def drag_and_drop(self):
        # First get items positions
        elems = self.selenium.find_elements(By.CSS_SELECTOR, '.grid-item img')
        positions = [elem.rect for elem in elems]

        # Then enable features
        checkbox = self.selenium.find_element(By.ID, 'draggable-switch')
        checkbox.click()

        # Drag and drop element
        elems = self.selenium.find_elements(By.CLASS_NAME, 'grid-item')
        ActionChains(self.selenium) \
            .drag_and_drop(elems[1], elems[0])\
            .perform()

        # Finally, check that images are moved
        return WebDriverWait(self.selenium, 5).until(
            is_checked(positions),
        )

    def get_layout_items(self):
        items = []

        elems = WebDriverWait(self.selenium, 5, 0.25).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'grid-item'))
        )
        for elem in elems:
            try:
                # Image without page?
                elem.find_element(By.CLASS_NAME, 'grid-item-link')  # unecessary timeout...
            except NoSuchElementException:
                items.append({
                    'img_src': elem.find_element(By.TAG_NAME, 'img').get_property('currentSrc'),
                })
            else:
                items.append({
                    'title': elem.find_element(By.CLASS_NAME, 'post-title').get_dom_attribute('data-post-title'),
                    'href': elem.find_element(By.TAG_NAME, 'a').get_attribute('href'),
                    'img_src': elem.find_element(By.TAG_NAME, 'img').get_property('currentSrc'),
                })

        return items

    def resize_item(self):
        locator = (By.CLASS_NAME, 'grid-item')
        elem = self.selenium.find_element(*locator)

        # Click on grid item image ti got focus
        img = elem.find_element(By.TAG_NAME, 'img')
        img.click()

        button = elem.find_element(By.CSS_SELECTOR, '.grid-item-zoom button')
        WebDriverWait(self.selenium, 5).until(
            EC.visibility_of(button),
        )
        button.click()

        return WebDriverWait(self.selenium, 5).until(
            has_css_class(elem, 'grid-item--width2')
        )

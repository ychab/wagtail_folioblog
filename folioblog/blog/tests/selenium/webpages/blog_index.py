from selenium.webdriver.common.by import By

from folioblog.core.utils.tests.selenium import BaseIndexWebPage


class BlogIndexWebPage(BaseIndexWebPage):
    def scroll_down(self, expected_count):
        return super().scroll_down(
            (By.CSS_SELECTOR, ".grid-item"),
            expected_count,
        )

    def filter_category(self, slug, expected_count):
        return super().filter_category(
            (By.ID, "blog-filter-category"),
            (By.CLASS_NAME, "grid-item"),
            slug,
            expected_count,
        )

    def get_grid_items(self):
        items = []

        elems = self.selenium.find_elements(By.CLASS_NAME, "grid-item")
        for elem in elems:
            items.append(
                {
                    "elem": elem,
                    "title": elem.find_element(By.TAG_NAME, "a").text,
                    "link": elem.find_element(By.TAG_NAME, "a").get_attribute("href"),
                    "category": elem.find_element(By.CLASS_NAME, "post-category").text,
                    "date": elem.find_element(By.CLASS_NAME, "post-date").text,
                    "intro": elem.find_element(By.CLASS_NAME, "post-intro").text,
                    "img_src": elem.find_element(By.TAG_NAME, "img").get_property("currentSrc"),
                }
            )

        return items

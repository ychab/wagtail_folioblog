from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import all_of
from selenium.webdriver.support.wait import WebDriverWait

from folioblog.core.utils.tests.selenium import BaseIndexWebPage, is_scroll_finished
from folioblog.search.tests.selenium.conditions import is_autocompleted


class SearchIndexWebPage(BaseIndexWebPage):
    def scroll_to_form(self):
        return self.scroll_to((By.ID, "search-form"))

    def scroll_to_results(self, expected_count):
        locator = (By.CSS_SELECTOR, ".search-results-item:last-child")
        is_scrolled = self.scroll_to(locator)

        # Then wait for infinite scroll to load items.
        is_finished = WebDriverWait(self.selenium, 5).until(
            is_scroll_finished((By.CLASS_NAME, "search-results-item"), expected_count),
        )
        return is_scrolled and is_finished

    def submit_form(self):
        form = self.selenium.find_element(By.CSS_SELECTOR, "#search-form form")
        form.submit()

        return WebDriverWait(self.selenium, 5).until(EC.presence_of_element_located((By.ID, "search-results")))

    def search(self, query):
        input = self.selenium.find_element(By.ID, "search-query")
        input.clear()
        input.send_keys(query)
        return self.submit_form()

    def autocomplete(self, query):
        input = self.selenium.find_element(By.ID, "search-query")
        input.clear()
        input.send_keys(query)

        WebDriverWait(self.selenium, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#autocomplete-results ul li"))
        )

        items = []
        elems = self.selenium.find_elements(By.CSS_SELECTOR, "#autocomplete-results ul li")
        for elem in elems:
            items.append(
                {
                    "elem": elem,
                    "id": elem.get_attribute("id"),
                    "title": elem.find_element(By.TAG_NAME, "button").text,
                    "href": elem.find_element(By.TAG_NAME, "a").get_attribute("href"),
                }
            )

        return items

    def autocomplete_select(self, item):
        button = item["elem"].find_element(By.TAG_NAME, "button")
        button.click()

        return WebDriverWait(self.selenium, 5).until(is_autocompleted(item["title"]))

    def autocomplete_goto(self, item):
        link = item["elem"].find_element(By.TAG_NAME, "a")
        link.click()

        WebDriverWait(self.selenium, 5).until(
            all_of(
                EC.title_is(item["title"]),
                EC.url_to_be(item["href"]),
            )
        )

        return self.selenium.title

    def tag_autocomplete(self, text):
        input = self.selenium.find_element(By.CLASS_NAME, "tagify__input")
        input.clear()
        input.send_keys(text)

        return WebDriverWait(self.selenium, 5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "tagify__dropdown")),
        )

    def tag_autocomplete_select(self, elem):  # pragma: no cover
        WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable(elem),
        )
        # @TODO - fixme: obvisouly, another element is receiving the click event?
        elem.click()

        return WebDriverWait(self.selenium, 5, 1).until(
            all_of(
                EC.invisibility_of_element_located((By.CLASS_NAME, "tagify__dropdown")),
                EC.visibility_of_element_located((By.CLASS_NAME, "tagify__tag-text")),
            )
        )

    def tag_autocomplete_select_keys(self, count, expected_value):
        input = self.selenium.find_element(By.CLASS_NAME, "tagify__input")
        for i in range(0, count):
            input.send_keys(Keys.DOWN)
        input.send_keys(Keys.ENTER)

        return WebDriverWait(self.selenium, 5).until(
            EC.presence_of_element_located((By.XPATH, f'//tags/tag[@value="{expected_value}"]')),
        )

    def get_tag_items(self):
        items = []

        list = self.selenium.find_element(By.CLASS_NAME, "tagify__dropdown")  # needs to be reloaded
        elems = list.find_elements(By.CLASS_NAME, "tagify__dropdown__item")
        for elem in elems:
            items.append(
                {
                    "elem": elem,
                    "value": elem.get_attribute("value"),
                }
            )

        return items

    def filter_tag(self, category):  # pragma: no cover
        self.tag_autocomplete(category)

        items = self.get_tag_items()
        self.tag_autocomplete_select(items[0]["elem"])

        self.submit_form()
        return self.get_search_results()

    def filter_category(self, category):
        # Unfortunetly, we cannot click on checkboxes (hidden in UI).
        label = self.selenium.find_element(By.XPATH, f'//label[@for="cat-{category}"]')
        label.click()
        return self.submit_form()

    def get_search_results(self):
        items = []

        elems = self.selenium.find_elements(By.CLASS_NAME, "search-results-item")
        for elem in elems:
            items.append(
                {
                    "href": elem.find_element(By.TAG_NAME, "a").get_attribute("href"),
                    "title": elem.find_element(By.CLASS_NAME, "post-title").text,
                    "subtitle": elem.find_element(By.CLASS_NAME, "post-subtitle").text,
                    "intro": elem.find_element(By.CLASS_NAME, "post-intro").text,
                    "img_src": elem.find_element(By.TAG_NAME, "img").get_property("currentSrc"),
                    "tags": elem.find_element(By.CLASS_NAME, "post-tags").text,
                }
            )

        return items

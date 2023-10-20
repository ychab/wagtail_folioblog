import logging
import os
from tempfile import mkstemp

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import all_of
from selenium.webdriver.support.wait import WebDriverWait

from folioblog.core.utils.tests.selenium import is_document_ready
from folioblog.core.utils.tests.selenium.conditions import (
    has_active_class,
    is_not_obstructed,
    is_scroll_finished,
    is_visible_in_viewport,
    videos_stopped,
)

logger = logging.getLogger(__name__)


class BaseIndexWebPage:
    def __init__(self, selenium: RemoteWebDriver) -> None:
        self.selenium: RemoteWebDriver = selenium

    def fetch_page(self, url, timeout=2, skip_check_url=False, force_consent=True):
        # First of all, fetch the page
        self.selenium.get(url)

        # Then do implicit wait manually to don't mix with explicit wait.
        # @see https://www.selenium.dev/documentation/webdriver/waits/#implicit-wait
        conditions = [
            EC.invisibility_of_element_located(
                (By.ID, "page-500-body")
            ),  # check for 500 page
            is_document_ready(),
        ]
        if not skip_check_url:
            conditions.append(EC.url_to_be(url))

        is_fetched = WebDriverWait(self.selenium, timeout).until(all_of(*conditions))

        # First time browser hit a page, se we needs to refresh it for new cookie.
        if is_fetched and force_consent:
            self.cookies_accept()

        return is_fetched

    def cookies_accept(self):
        if self.has_cookie_consent():
            return True

        button = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, "cookies-eu-accept")),
        )
        button.click()

        return WebDriverWait(self.selenium, 5).until(
            EC.invisibility_of_element_located((By.ID, "cookies-eu-banner")),
        )

    def cookies_reject(self):
        if self.has_cookie_consent() is not None:
            return True

        button = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable((By.ID, "cookies-eu-reject")),
        )
        button.click()

        return WebDriverWait(self.selenium, 5).until(
            EC.invisibility_of_element_located((By.ID, "cookies-eu-banner"))
        )

    def force_cookie_consent(self, value="true"):
        self.selenium.add_cookie(
            {
                "name": "hasConsent",
                "value": value,
                "path": "/",
            }
        )

    def cookie_consent_reset(self):
        self.selenium.delete_cookie("hasConsent")

    def has_cookie_banner(self):
        try:
            return WebDriverWait(self.selenium, 1).until(
                EC.visibility_of_element_located((By.ID, "cookies-eu-banner"))
            )
        except TimeoutException:
            return False

    def has_cookie_consent(self):
        cookie = self.selenium.get_cookie("hasConsent")
        if cookie is not None:
            return cookie.get("value") == "true"

    def has_cookie_consent_banner(self):
        return WebDriverWait(self.selenium, 2).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "youtube-cookies-consent"))
        )

    def save_screenshot(self, screenshot_dir, prefix="screenshot"):
        fd, filename = mkstemp(prefix=prefix + "-", suffix=".png")
        filepath = os.path.join(
            screenshot_dir,
            os.path.basename(filename),
        )
        return self.selenium.save_screenshot(filepath)

    def scroll_to(self, locator):
        # Wait for element if not yet loaded
        elem = WebDriverWait(self.selenium, 5).until(
            EC.presence_of_element_located(locator)
        )

        # Scroll into view with JS! Beurk!! But whyyyy??
        # Because  we could ONLY check in JS if element is visible into the
        # viewport. Obviously, WebElement.rect is relative to the WINDOW, not
        # the viewport. In other words, it would NEVER change, no matter if we
        # scroll into the page or not... So now, because we need JS to know the
        # position of the element into the viewport, we could also use it to
        # scroll into the page and be sure that we use the same variables!
        # By the way:
        # - ActionChains.scroll_to_element() is not always working
        # - ActionChains.scroll_by_amount() always work, but need the current
        #   position of the viewport in JS to calculate the delta Y...
        elem.location_once_scrolled_into_view

        return WebDriverWait(self.selenium, 5).until(
            all_of(
                is_visible_in_viewport(elem),
                is_not_obstructed(elem),
            )
        )

    def scroll_to_top(self):
        return self.scroll_to((By.TAG_NAME, "header"))

    def scroll_to_video(self, locator=None):
        locator = locator or (By.CLASS_NAME, "video-youtube-thumbnail")
        return self.scroll_to(locator)

    def scroll_down(self, locator, expected_count):
        # First scroll to latest element.
        last_locator = (locator[0], locator[1] + ":last-child")
        is_scrolled = self.scroll_to(last_locator)

        # Then wait for infinite scroll to load items.
        is_finished = WebDriverWait(self.selenium, 5).until(
            is_scroll_finished(locator, expected_count),
        )

        return is_scrolled and is_finished

    def filter_category(self, button_locator, item_locator, slug, expected_count):
        button = self.selenium.find_element(*button_locator)
        button.click()

        link_locator = [By.XPATH, f'//a[@data-filter="category-{slug}"]']
        link = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable(link_locator)
        )
        link.click()

        return WebDriverWait(self.selenium, 5).until(
            all_of(
                has_active_class(link_locator),
                is_scroll_finished(item_locator, expected_count),
            )
        )

    def play_video(self, locator=None):
        locator = locator or (By.CLASS_NAME, "youtube-player-button")

        button = WebDriverWait(self.selenium, 5).until(
            EC.element_to_be_clickable(locator),
        )
        button.click()

        # First wait for thumbnail to disappear.
        is_triggered = WebDriverWait(self.selenium, 2).until(
            EC.invisibility_of_element_located(button)
        )

        # Then wait for YouTube to insert the iframe.
        try:
            is_loaded = WebDriverWait(self.selenium, 5).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".video-youtube-player-wrapper iframe")
                )
            )
        except TimeoutException:  # pragma: no cover
            # Because YouTube maybe very slow, we won't wait indefinitely...
            is_loaded = False

        return is_triggered, is_loaded

    def stop_videos(self):
        locator = (By.CLASS_NAME, "video-youtube-player-wrapper")
        elems = self.selenium.find_elements(*locator)
        video_ids = [elem.get_attribute("data-video-id") for elem in elems]

        # Beautifuuuuuul... I just want U to know... U'R my favorite giiiiirl
        self.selenium.execute_script(
            """
            for (let playerId in youtubePlayers) {
                youtubePlayers[playerId].destroy();
                delete youtubePlayers[playerId];
            }
        """
        )

        return WebDriverWait(self.selenium, 5).until(
            all_of(*[videos_stopped(vid) for vid in video_ids])
        )

    def stop_video(self, locator=None):
        locator = locator or (By.CLASS_NAME, "video-youtube-player-wrapper")
        elem = self.selenium.find_element(*locator)
        video_id = elem.get_attribute("data-video-id")

        # Beautifuuuuuul... I just want U to know... U'R my favorite giiiiirl
        self.selenium.execute_script(
            """
            for (let playerId in youtubePlayers) {
                if (playerId == arguments[0]) {
                    youtubePlayers[playerId].destroy();
                    delete youtubePlayers[playerId];
                }
            }
        """,
            video_id,
        )

        return WebDriverWait(self.selenium, 5).until(
            lambda driver: driver.find_element(
                By.ID, f"youtube-video-{video_id}"
            ).tag_name
            == "div"
        )

    def get_url(self):
        return self.selenium.current_url

    url = property(get_url)

    def get_title(self):
        return self.selenium.title

    title = property(get_title)

    def get_content(self):
        return self.selenium.page_source

    content = property(get_content)

    def get_masterhead_image(self):
        elem = self.selenium.find_element(By.CLASS_NAME, "masthead")
        return (
            elem.value_of_css_property("background-image")
            .replace('url("', "")
            .replace('")', "")
        )


class BaseWebPage(BaseIndexWebPage):
    def get_related_pages(self):
        data = []

        elems = self.selenium.find_elements(By.CLASS_NAME, "related-page")
        for elem in elems:
            data.append(
                {
                    "title": elem.find_element(
                        By.CLASS_NAME, "related-page-title"
                    ).text,
                    "url": elem.find_element(
                        By.CLASS_NAME, "related-page-link"
                    ).get_attribute("href"),
                    "img_src": elem.find_element(By.TAG_NAME, "img").get_property(
                        "currentSrc"
                    ),
                }
            )

        return data

    def get_image_with_caption(self):
        elem = self.selenium.find_element(By.CLASS_NAME, "page-image")
        return {
            "img_src": elem.find_element(By.TAG_NAME, "img").get_property("currentSrc"),
            "caption": elem.find_element(By.TAG_NAME, "figcaption").text,
        }

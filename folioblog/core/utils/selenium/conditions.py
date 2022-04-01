from selenium.webdriver.common.by import By


def is_document_ready():

    def _is_document_ready(driver):
        return driver.execute_script('return document.readyState') == 'complete'

    return _is_document_ready


def is_visible_in_viewport(elem):
    """
    It wasn't me!
    @see https://medium.com/bliblidotcom-techblog/how-to-create-custom-expectedcondition-to-check-whether-an-element-within-web-viewport-not-on-fad42bc4d0f9  # noqa
    """

    def _is_element_in_viewport(driver):
        return driver.execute_script("""
            var element = arguments[0];
            var rect = element.getBoundingClientRect();
            return (
                rect.top >= 0 &&
                rect.left >= 0 &&
                rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                rect.right <= (window.innerWidth || document.documentElement.clientWidth)
            );
        """, elem)

    return _is_element_in_viewport


def is_not_obstructed(elem):
    """
    It wasn't me!
    @see https://medium.com/bliblidotcom-techblog/how-to-create-custom-expectedcondition-to-check-whether-an-element-within-web-viewport-not-on-fad42bc4d0f9  # noqa
    """

    def _is_not_obstructed(driver):
        return driver.execute_script("""
            var element = arguments[0];
            var rect = element.getBoundingClientRect();
            var cx = rect.left + rect.width / 2;
            var cy = rect.top + rect.height / 2;
            var el = document.elementFromPoint(cx, cy);
            var isNotObstructed = false;
            for(; el; el = el.parentElement) {
                if (el === element) {
                    isNotObstructed = true;
                    break;
                }
            }
            return isNotObstructed;
        """, elem)

    return _is_not_obstructed


def has_count_expected(locator, expected_count):

    def _has_count_expected(driver):
        elems = driver.find_elements(*locator)
        for elem in elems:
            if not elem.is_displayed():  # pragma: no cover
                return False
        return len(elems) == expected_count

    return _has_count_expected


def is_scroll_finished(locator, expected_count):
    return has_count_expected(locator, expected_count)


def has_css_class_located(locator, css_class):

    def _has_css_class_located(driver):
        return css_class in driver.find_element(*locator).get_attribute('class')

    return _has_css_class_located


def has_css_class(elem, css_class):

    def _has_css_class(driver):
        return css_class in elem.get_attribute('class')

    return _has_css_class


def has_active_class(locator):
    return has_css_class_located(locator, 'active')


def videos_stopped(video_id):

    def _videos_stopped(driver):
        return driver.find_element(By.ID, f'youtube-video-{video_id}').tag_name == 'div'

    return _videos_stopped

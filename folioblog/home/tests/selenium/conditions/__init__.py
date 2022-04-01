from selenium.webdriver.common.by import By


def player_thumbnail_match(src):

    def _is_player_thumbnail(driver):
        elem = driver.find_element(By.CLASS_NAME, 'video-youtube-thumbnail img')
        return src in elem.get_property('currentSrc')

    return _is_player_thumbnail


def player_link_match(href):

    def _is_player_link(driver):
        elem = driver.find_element(By.CLASS_NAME, 'video-title-link')
        return href in elem.get_attribute('href')

    return _is_player_link

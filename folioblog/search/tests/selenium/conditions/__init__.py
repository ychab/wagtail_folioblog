from selenium.webdriver.common.by import By


def is_autocompleted(text):

    def _is_autocompleted(driver):
        return driver.find_element(By.ID, 'search-query').get_attribute('value') == text

    return _is_autocompleted

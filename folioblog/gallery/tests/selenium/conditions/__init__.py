from selenium.webdriver.common.by import By


def is_checked(positions):

    def _is_checked(driver):
        elems = driver.find_elements(By.CSS_SELECTOR, '.grid-item img')
        new_positions = [elem.rect for elem in elems]
        return positions != new_positions

    return _is_checked

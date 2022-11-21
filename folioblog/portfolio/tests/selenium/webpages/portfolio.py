from selenium.webdriver.common.by import By

from folioblog.core.utils.tests.selenium import BaseIndexWebPage


class PortFolioWebPage(BaseIndexWebPage):

    def get_service_items(self):
        items = []

        elems = self.selenium.find_elements(By.CSS_SELECTOR, '#services .service-item')
        for elem in elems:
            items.append({
                'name': elem.find_element(By.CLASS_NAME, 'service-name').text,
                'text': elem.find_element(By.CLASS_NAME, 'service-text').text,
                'items': elem.find_element(By.CLASS_NAME, 'service-items').text,
            })

        return items

    def get_skill_items(self):
        items = []

        elems = self.selenium.find_elements(By.CSS_SELECTOR, '#portfolio .skill-item')
        for elem in elems:
            items.append({
                'heading': elem.find_element(By.CLASS_NAME, 'skill-heading').text,
                'subheading': elem.find_element(By.CLASS_NAME, 'skill-subheading').text,
                'img_src': elem.find_element(By.TAG_NAME, 'img').get_property('currentSrc'),
            })

        return items

    def get_experience_items(self):
        items = []

        elems = self.selenium.find_elements(By.CSS_SELECTOR, '#cv .experience-item')
        for elem in elems:
            items.append({
                'date': elem.find_element(By.CLASS_NAME, 'experience-date').text,
                'company': elem.find_element(By.CLASS_NAME, 'experience-company').text,
                'text': elem.find_element(By.CLASS_NAME, 'experience-text').text,
                'img_src': elem.find_element(By.TAG_NAME, 'img').get_property('currentSrc'),
            })

        return items

    def get_member_items(self):
        items = []

        elems = self.selenium.find_elements(By.CSS_SELECTOR, '#team .team-member')
        for elem in elems:
            items.append({
                'name': elem.find_element(By.CLASS_NAME, 'team-member-name').text,
                'job': elem.find_element(By.CLASS_NAME, 'team-member-job').text,
                'img_src': elem.find_element(By.TAG_NAME, 'img').get_property('currentSrc'),
            })

        return items

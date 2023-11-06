from django.test import TestCase


class MultiDomainPageTestCase(TestCase):
    site = None
    root_page = None
    root_page_original = None

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.root_page_original = cls.site.root_page
        cls.site.root_page = cls.root_page
        cls.site.save()

    @classmethod
    def tearDownClass(cls):
        # Because we change the site root page which is created by migrations,
        # it would affect next TestCases even if rollback is done because the
        # root page was done BEFORE entering into the SQL transaction.
        # As a result, we need to reset it manually.
        cls.site.root_page = cls.root_page_original
        cls.site.save(update_fields=["root_page"])
        super().tearDownClass()

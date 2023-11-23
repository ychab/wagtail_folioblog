from unittest import TestCase

from folioblog.core.utils.richtext import richtext_extract_image_attrs


class RichTextUtilsTestCase(TestCase):
    def test_extract_image_no_match(self):
        self.assertIsNone(richtext_extract_image_attrs(0, ""))

    def test_extract_image_wrong_type(self):
        html = '<embed alt="Foo" embedtype="media" url="http://example.com" id="0"/>'
        self.assertIsNone(richtext_extract_image_attrs(0, html))

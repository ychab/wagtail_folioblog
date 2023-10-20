from django.test import TestCase

from wagtail.images import get_image_model

from wagtail_factories import CollectionFactory

from folioblog.core.factories import ImageFactory

Image = get_image_model()


class ImageModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.image = ImageFactory()

    def test_collection_changed(self):
        col1 = CollectionFactory(name="foo")
        col2 = CollectionFactory(name="bar")

        image = ImageFactory(collection=col1)
        rendition = image.get_rendition("fill-400x300")
        self.assertIn("foo", rendition.url)

        image.collection = col2
        image.save()

        self.assertEqual(image.renditions.count(), 1)
        rendition = image.renditions.first()
        self.assertIn("bar", rendition.url)

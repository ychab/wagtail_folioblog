from datetime import timedelta

from django.utils import timezone
from django.utils.translation import get_language, gettext_lazy as _, to_locale

from wagtail.embeds.embeds import get_embed_hash
from wagtail.embeds.models import Embed

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from wagtail_factories import PageFactory

from folioblog.core.factories import (
    BaseCategoryFactory, BaseIndexPageFactory, BasePageFactory, BaseTagFactory,
    ImageFactory,
)
from folioblog.video.models import (
    VideoCategory, VideoIndexPage, VideoPage, VideoPageRelatedLink,
    VideoPageTag, VideoPromote, VideoPromoteLink, VideoTag,
)

current_locale = to_locale(get_language())


class VideoIndexPageFactory(BaseIndexPageFactory):

    class Meta:
        model = VideoIndexPage

    title = _('Vidéos')
    slug = 'videos'


class VideoCategoryFactory(BaseCategoryFactory):

    class Meta:
        model = VideoCategory


class VideoTagFactory(BaseTagFactory):

    class Meta:
        model = VideoTag


class EmbedFactory(DjangoModelFactory):

    class Meta:
        model = Embed
        django_get_or_create = ('hash',)
        skip_postgeneration_save = True

    url = factory.Faker('url')
    max_width = fuzzy.FuzzyInteger(400, 800)
    hash = factory.lazy_attribute(lambda o: get_embed_hash(o.url))
    type = 'video'
    html = '<iframe></iframe>'
    title = factory.Faker('sentence', locale=current_locale)
    author_name = factory.Faker('name', locale=current_locale)
    provider_name = 'YouTube'
    thumbnail_url = factory.Faker('image_url')
    width = fuzzy.FuzzyInteger(200, 800)
    height = fuzzy.FuzzyInteger(200, 800)
    last_updated = fuzzy.FuzzyDateTime(
        start_dt=timezone.now() - timedelta(days=3),
        end_dt=timezone.now(),
    )


class VideoPageRelatedLinkFactory(DjangoModelFactory):

    class Meta:
        model = VideoPageRelatedLink
        skip_postgeneration_save = True

    page = factory.SubFactory('folioblog.video.factories.VideoPageFactory')
    related_page = factory.SubFactory(PageFactory)


class VideoPageFactory(BasePageFactory):

    class Meta:
        model = VideoPage

    title = factory.Sequence(lambda n: 'video_{n}'.format(n=n))

    date = fuzzy.FuzzyDateTime(timezone.now())
    category = factory.SubFactory(VideoCategoryFactory)
    video_url = factory.Faker('youtube_url', locale=current_locale)
    thumbnail = factory.SubFactory(ImageFactory, file__width=480, file__height=360)

    @factory.post_generation
    def tags(obj, create, extracted, **kwargs):
        if create:  # pragma: no branch
            tags = []

            if extracted:
                tags = extracted
            elif kwargs.get('number', 0) > 0:
                tags = [VideoTagFactory() for i in range(0, kwargs['number'])]

            for tag in tags:
                VideoPageTagFactory(tag=tag, content_object=obj)

    @factory.post_generation
    def embed(obj, create, extracted, **kwargs):
        # Because embed will be first created on the fly and may raise network
        # issue during testing, we generate it first before any hits and avoid
        # network call on YouTube!
        if create and not kwargs.get('skip', False):  # pragma: no branch
            EmbedFactory(url=obj.video_url)

    @factory.post_generation
    def promoted(obj, create, extracted, **kwargs):
        if create and extracted:
            VideoPromoteLinkFactory(related_page=obj)

    @factory.post_generation
    def related_pages(obj, create, extracted, **kwargs):
        if create:  # pragma: nobranch
            related_pages = []

            if extracted:
                related_pages = extracted
            elif kwargs.get('number', 0) > 0:
                related_pages = [
                    VideoPageFactory(parent=obj.get_parent()) for i in range(0, kwargs['number'])
                ]

            for page in related_pages:
                VideoPageRelatedLinkFactory(page=obj, related_page=page)


class VideoPageTagFactory(DjangoModelFactory):

    class Meta:
        model = VideoPageTag
        django_get_or_create = ('tag', 'content_object')
        skip_postgeneration_save = True

    tag = factory.SubFactory(VideoTagFactory)
    content_object = factory.SubFactory(VideoPageFactory)


class VideoPromoteFactory(DjangoModelFactory):

    class Meta:
        model = VideoPromote
        django_get_or_create = ('title',)  # just for reuse in testing
        skip_postgeneration_save = True

    title = factory.Faker('sentence', locale=current_locale)
    link_more = factory.Faker('sentence', locale=current_locale)


class VideoPromoteLinkFactory(DjangoModelFactory):

    class Meta:
        model = VideoPromoteLink
        skip_postgeneration_save = True

    snippet = factory.SubFactory(VideoPromoteFactory, title='videos')
    related_page = factory.SubFactory(VideoPageFactory)

    @factory.lazy_attribute
    def sort_order(self):
        """
        A better option would be to override _setup_next_sequence() but just for
        the example (and because we don't use it a lot), we keep it as it!
        """
        link = VideoPromoteLink.objects \
            .filter(snippet__title='videos') \
            .order_by('-sort_order')[:1] \
            .first()
        return link.sort_order + 1 if link else 0

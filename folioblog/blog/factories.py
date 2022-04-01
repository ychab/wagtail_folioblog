from django.utils import timezone
from django.utils.translation import get_language, gettext_lazy as _, to_locale

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from wagtail_factories import PageFactory

from folioblog.blog.models import (
    BlogCategory, BlogIndexPage, BlogPage, BlogPageRelatedLink, BlogPageTag,
    BlogPromote, BlogPromoteLink, BlogTag,
)
from folioblog.core.factories import (
    BaseCategoryFactory, BaseIndexPageFactory, BasePageFactory, BaseTagFactory,
)

current_locale = to_locale(get_language())


class BlogCategoryFactory(BaseCategoryFactory):

    class Meta:
        model = BlogCategory

    name = fuzzy.FuzzyChoice(['tech', 'economie', 'philosophie'])


class BlogTagFactory(BaseTagFactory):

    class Meta:
        model = BlogTag


class BlogIndexPageFactory(BaseIndexPageFactory):

    class Meta:
        model = BlogIndexPage

    title = _('Articles')
    slug = 'posts'


class BlogPageRelatedLinkFactory(DjangoModelFactory):

    class Meta:
        model = BlogPageRelatedLink

    page = factory.SubFactory('folioblog.blog.factories.BlogPageFactory')
    related_page = factory.SubFactory(PageFactory)


class BlogPageFactory(BasePageFactory):

    class Meta:
        model = BlogPage

    date = fuzzy.FuzzyDateTime(timezone.now())
    category = factory.SubFactory(BlogCategoryFactory)

    blockquote = factory.Faker('sentence', nb_words=5, locale=current_locale)
    blockquote_author = factory.Faker('name', locale=current_locale)
    blockquote_ref = factory.Faker('word', locale=current_locale)

    @factory.post_generation
    def tags(obj, create, extracted, **kwargs):
        if create:  # pragma: no branch
            tags = []

            if extracted:
                tags = extracted
            elif kwargs.get('number', 0) > 0:
                tags = [BlogTagFactory() for i in range(0, kwargs['number'])]

            for tag in tags:
                BlogPageTagFactory(tag=tag, content_object=obj)

    @factory.post_generation
    def related_pages(obj, create, extracted, **kwargs):
        if create:  # pragma: nobranch
            related_pages = []

            if extracted:
                related_pages = extracted
            elif kwargs.get('number', 0) > 0:
                related_pages = [
                    BlogPageFactory(parent=obj.get_parent()) for i in range(0, kwargs['number'])
                ]

            for page in related_pages:
                BlogPageRelatedLinkFactory(page=obj, related_page=page)

    @factory.post_generation
    def promoted(obj, create, extracted, **kwargs):
        if create and extracted:
            BlogPromoteLinkFactory(related_page=obj)


class BlogPageTagFactory(DjangoModelFactory):

    class Meta:
        model = BlogPageTag
        django_get_or_create = ('tag', 'content_object')

    tag = factory.SubFactory(BlogTagFactory)
    content_object = factory.SubFactory(BlogPageFactory)


class BlogPromoteFactory(DjangoModelFactory):

    class Meta:
        model = BlogPromote
        django_get_or_create = ('title',)  # just for reuse in testing

    title = factory.Faker('sentence', locale=current_locale)
    link_more = factory.Faker('sentence', locale=current_locale)


class BlogPromoteLinkFactory(DjangoModelFactory):

    class Meta:
        model = BlogPromoteLink

    snippet = factory.SubFactory(BlogPromoteFactory, title='blog')
    related_page = factory.SubFactory(BlogPageFactory)

    @factory.lazy_attribute
    def sort_order(self):
        """
        A better option would be to override _setup_next_sequence() but just for
        the example (and because we don't use it a lot), we keep it as it!
        """
        link = BlogPromoteLink.objects\
            .filter(snippet__title='blog')\
            .order_by('-sort_order')[:1]\
            .first()
        return link.sort_order + 1 if link else 0

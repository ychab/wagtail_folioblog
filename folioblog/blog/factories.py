from django.utils import timezone
from django.utils.translation import get_language, to_locale

from wagtail.models import Site

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory
from wagtail_factories import PageFactory

from folioblog.blog.models import (
    BlogCategory,
    BlogIndexPage,
    BlogPage,
    BlogPageRelatedLink,
    BlogPageTag,
    BlogPromote,
    BlogPromoteLink,
    BlogTag,
)
from folioblog.core.factories import (
    BaseCategoryFactory,
    BaseIndexPageFactory,
    BasePageFactory,
    BaseTagFactory,
)

current_locale = to_locale(get_language())


class BlogCategoryFactory(BaseCategoryFactory):
    class Meta:
        model = BlogCategory

    name = fuzzy.FuzzyChoice(["tech", "economie", "philosophie"])


class BlogTagFactory(BaseTagFactory):
    class Meta:
        model = BlogTag


class BlogIndexPageFactory(BaseIndexPageFactory):
    class Meta:
        model = BlogIndexPage

    title = "Posts"
    slug = "posts"


class BlogPageRelatedLinkFactory(DjangoModelFactory):
    class Meta:
        model = BlogPageRelatedLink
        skip_postgeneration_save = True

    page = factory.SubFactory("folioblog.blog.factories.BlogPageFactory")
    related_page = factory.SubFactory(PageFactory)


class BlogPageFactory(BasePageFactory):
    class Meta:
        model = BlogPage

    title = factory.Sequence(lambda n: "post_{n}".format(n=n))

    date = fuzzy.FuzzyDateTime(timezone.now())

    category = factory.SubFactory(
        BlogCategoryFactory,
        # WARNING - using get_site() here cause cache in page url sites...
        site=factory.LazyAttribute(lambda o: o.factory_parent.parent.get_site()),
    )

    blockquote = factory.Faker("sentence", nb_words=5, locale=current_locale)
    blockquote_author = factory.Faker("name", locale=current_locale)
    blockquote_ref = factory.Faker("word", locale=current_locale)

    @factory.post_generation
    def tags(obj, create, extracted, **kwargs):
        if create:  # pragma: no branch
            tags = []

            if extracted:
                tags = extracted
            elif kwargs.get("number", 0) > 0:
                tags = [
                    BlogTagFactory(site=obj.get_site())
                    for _ in range(0, kwargs["number"])
                ]

            for tag in tags:
                BlogPageTagFactory(tag=tag, content_object=obj)

    @factory.post_generation
    def related_pages(obj, create, extracted, **kwargs):
        if create:  # pragma: nobranch
            related_pages = []
            number = kwargs.pop("number", False)

            if extracted:
                related_pages = extracted
            elif number:
                related_pages = [
                    BlogPageFactory(parent=obj.get_parent(), **kwargs)
                    for _ in range(0, number)
                ]

            for page in related_pages:
                BlogPageRelatedLinkFactory(page=obj, related_page=page)

    @factory.post_generation
    def promoted(obj, create, extracted, **kwargs):
        if create and extracted:
            BlogPromoteLinkFactory(related_page=obj, snippet__site=obj.get_site())


class BlogPageTagFactory(DjangoModelFactory):
    class Meta:
        model = BlogPageTag
        django_get_or_create = ("tag", "content_object")
        skip_postgeneration_save = True

    tag = factory.SubFactory(BlogTagFactory)
    content_object = factory.SubFactory(BlogPageFactory)


class BlogPromoteFactory(DjangoModelFactory):
    class Meta:
        model = BlogPromote
        django_get_or_create = ("title", "site")  # just for reuse in testing
        skip_postgeneration_save = True

    title = factory.Faker("sentence", locale=current_locale)
    link_more = factory.Faker("sentence", locale=current_locale)
    site = factory.LazyFunction(lambda: Site.objects.get(is_default_site=True))


class BlogPromoteLinkFactory(DjangoModelFactory):
    class Meta:
        model = BlogPromoteLink
        skip_postgeneration_save = True

    snippet = factory.SubFactory(BlogPromoteFactory, title="blog")
    related_page = factory.SubFactory(BlogPageFactory)

    @factory.lazy_attribute
    def sort_order(self):
        """
        A better option would be to override _setup_next_sequence() but just for
        the example (and because we don't use it a lot), we keep it as it!
        """
        link = (
            BlogPromoteLink.objects.filter(snippet__title="blog")
            .order_by("-sort_order")[:1]
            .first()
        )
        return link.sort_order + 1 if link else 0

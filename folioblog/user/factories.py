from django.contrib.auth import get_user_model
from django.utils.translation import get_language, to_locale

import factory
from factory.django import DjangoModelFactory

User = get_user_model()
current_locale = to_locale(get_language())


class UserFactory(DjangoModelFactory):

    class Meta:
        model = User
        django_get_or_create = ('username',)
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: 'user_{n}'.format(n=n))
    email = factory.LazyAttribute(lambda o: 'test+{o.username}@yannickchabbert.fr'.format(o=o))
    password = factory.django.Password('test')
    first_name = factory.Faker('first_name', locale=current_locale)
    last_name = factory.Faker('last_name', locale=current_locale)

    @classmethod
    def _setup_next_sequence(cls):
        """
        Ensure that sequence username generated is unique.
        """
        try:
            u = User.objects.filter(username__startswith='user_').order_by('-username')[:1][0]
        except IndexError:
            return 1
        else:
            return int(u.username.split('_')[1]) + 1

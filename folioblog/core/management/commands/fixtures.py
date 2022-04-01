import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

from folioblog.core.utils.fixtures import fixtures_map

User = get_user_model()


class Command(BaseCommand):
    fixtures = fixtures_map

    def add_arguments(self, parser):
        parser.add_argument('action', choices=['dump', 'load'])

    def handle(self, action, *args, **options):
        if action == 'load':
            fixtures = list(self.fixtures.keys())
            fixtures = [f for f in fixtures if f not in ['users', 'contenttypes', 'locales']]
            call_command('loaddata', *fixtures)
        else:
            for fixture, model in self.fixtures.items():
                app, label = model.split('.')
                if app in ['auth', 'contenttypes', 'taggit', 'wagtailcore']:
                    app = 'core'

                basepath = os.path.join('folioblog', app, 'fixtures', f'{fixture}.json')
                filepath = os.path.join(settings.BASE_DIR, basepath)

                kwargs = {
                    'indent': 4,
                    'output': filepath,
                }
                if fixture in ['pages', 'blogpagetags']:
                    kwargs['natural_foreign'] = True

                self.stdout.write(f'Dump {model} > {basepath}')
                call_command('dumpdata', model,  **kwargs)

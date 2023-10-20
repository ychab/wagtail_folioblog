from django.core.management.base import BaseCommand

from taggit.models import Tag

from folioblog.blog.models import BlogTag
from folioblog.video.models import VideoTag


class Command(BaseCommand):
    def handle(self, *args, **options):
        models = {
            Tag: "taggit_taggeditem_items",
            BlogTag: "tagged_blogs",
            VideoTag: "tagged_videos",
        }

        count = 0
        for Model, relname in models.items():
            deleted, _ = Model.objects.filter(**{f"{relname}__isnull": True}).delete()
            count += deleted

        self.stdout.write(self.style.SUCCESS(f"{count} orphan tags deleted."))

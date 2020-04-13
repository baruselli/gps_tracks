from django.core.management.base import BaseCommand, CommandError
from tracks.utils import associate_photos_to_tracks
from tracks.models import Track, Photo
import os


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass
        # Positional arguments
        # parser.add_argument('ext', nargs='+', type=str)

        # Named (optional) arguments
        # parser.add_argument(
        #    '-ext',

    #  )

    def handle(self, *args, **options):
        associate_photos_to_tracks()

from django.core.management.base import BaseCommand, CommandError
from tracks.utils import generate_tracks
from tracks.models import Track
import os


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("ext", nargs=1, type=str)
        parser.add_argument("update", type=str, nargs="?", default=False)
        # Named (optional) arguments
        # parser.add_argument(
        #'-ext',
        #    '--update'
        # action='store_true',
        # dest='delete',
        # help='Delete poll instead of closing it',
        # )

    def handle(self, *args, **options):

        #print(options)
        if options["update"] == "update":
            update = True
        else:
            update = False
        if options["ext"]:
            extensions = options["ext"]
            #print("using extensions: " + str(extensions))
            generate_tracks(os.path.join("..", "data"), extensions, update=update)
        else:
            generate_tracks(
                os.path.join("..", "data"), ["kml", "kmz", "gpx"], update=update
            )

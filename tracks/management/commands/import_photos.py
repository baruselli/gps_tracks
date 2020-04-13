import os

from django.core.management.base import BaseCommand

from tracks.utils import import_photos


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


        #        if options['ext']:
        #            extensions=options['ext']
        #            print("using extensions: "+ str(extensions))
        #            generate_tracks(os.path.join("..","data"),extensions)
        #        else:
        path = os.path.join(settings.BASE_DIR, "static", "Camera")
        #print(path)
        import_photos(path)

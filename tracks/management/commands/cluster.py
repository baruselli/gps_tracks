from django.core.management.base import BaseCommand, CommandError
from tracks.utils import cluster
from tracks.models import Track
import os


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("n", nargs="+", type=str)

        # Named (optional) arguments
        parser.add_argument(
            "-ext",
            # action='store_true',
            # dest='delete',
            # help='Delete poll instead of closing it',
        )

    def handle(self, *args, **options):

        if options["n"]:
            n_clusters = options["n"]
        else:
            n_clusters = 10
        #print("n clusters: " + str(n_clusters[0]))
        cluster(int(n_clusters[0]))

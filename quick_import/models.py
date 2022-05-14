from django.db import models
from download.utils import google_drive_tracks, google_drive_photos, google_photos, download_tomtom, download_garmin
from import_app.utils import import_photos, generate_tracks
from photos.utils import associate_photos_to_tracks
from options.models import OptionSet
import logging
from django.conf import settings


logger = logging.getLogger("gps_tracks")

class ImportStep(models.Model):
    TYPE_CHOICES = [
        ("11_download_tracks","Download Tracks"),
        ("21_import_tracks","Import Tracks"),
        ("31_download_photos","Download Photos"),
        ("41_import_photos","Import Photos"),
        ("51_link_track_photos","Link Photos to Tracks"),
        ("52_link_all_track_photos","Link Photos to all Tracks"),
        ("53_link_track_all_photos","Link all Photos to Tracks"),
    ]

    name = models.CharField(max_length=255, verbose_name="Import Step Name", null=False, blank=False, unique=True)
    step_code = models.CharField(max_length=255, null=False, blank=False, unique=True)
    step_type = models.CharField(max_length=255, null=False, blank=False, unique=False, choices=TYPE_CHOICES)

    class Meta:
        ordering = ["step_type"]

    def __str__(self):
        return str(self.name)

    def is_ok(self):
        if self.step_code == "google_drive_tracks":
            return bool(OptionSet.get_option("GOOGLE_TRACKS_DIRS"))
        elif self.step_code == "google_drive_photos":
            return bool(OptionSet.get_option("GOOGLE_PHOTOS_DIRS"))
        elif self.step_code == "download_tomtom":
            return OptionSet.get_option("TOMTOM_USER") and OptionSet.get_option("TOMTOM_PASSWORD")
        elif self.step_code == "download_garmin":
            return OptionSet.get_option("GARMIN_USER") and OptionSet.get_option("GARMIN_PASSWORD")
        else:
            return True


class QuickImport(models.Model):
    name = models.CharField(max_length=255, verbose_name="Quick Import Name", null=False, blank=False, unique=True)
    steps = models.ManyToManyField(ImportStep,blank=True)
    active = models.BooleanField(default=True,blank=True)

    def __str__(self):
        return str(self.name)

    def is_ok(self):
        for step in self.steps.all():
            if not step.is_ok():
                return False
        return True

    def execute(self):
        logger.info("Start quick import %s" %self.name)

        downloaded_photos = []
        downloaded_tracks = []
        generated_tracks = []
        imported_photos = []

        for step in self.steps.all().order_by("step_type"):
            logger.info(step)
            # download tracks
            if step.step_code == "google_drive_tracks":
                downloaded_tracks += google_drive_tracks()
            elif step.step_code == "download_tomtom":
                downloaded_tracks += download_tomtom(ext="csv")
            elif step.step_code == "download_garmin":
                garmin_tracks = download_garmin()
                if garmin_tracks is None:
                    logger.warning("Error in download_garmin, stop here")
                    return
                downloaded_tracks += garmin_tracks
            # import tracks
            elif step.step_code == "generate_tracks":
                generated_tracks = generate_tracks(settings.TRACKS_DIR,files = downloaded_tracks, update=False)
            # downloaded photos
            elif step.step_code == "google_drive_photos":
                downloaded_photos += google_drive_photos()
            elif step.step_code == "google_photos":
                downloaded_photos += google_photos(only_last_year=False)
            # import photos
            elif step.step_code == "import_photos":
                imported_photos = import_photos(files=downloaded_photos, update=True)
            # link photos - tracks
            # downloaded photos to downloaded tracks
            elif step.step_code == "associate_photos_to_tracks":
                associate_photos_to_tracks(photo_list=imported_photos, track_list=generated_tracks)
            # downloaded photos to all tracks
            elif step.step_code == "associate_photos_to_all_tracks":
                associate_photos_to_tracks(photo_list=imported_photos, track_list=None)
            # all photos to downloaded tracks
            elif step.step_code == "associate_all_photos_to_tracks":
                associate_photos_to_tracks(photo_list=[], track_list=generated_tracks)

        logger.info("downloaded_tracks")
        logger.info(downloaded_tracks)
        logger.info("generated_tracks")
        logger.info(generated_tracks)
        logger.info("downloaded_photos")
        logger.info(downloaded_photos)
        logger.info("imported_photos")
        logger.info([p.name for p in imported_photos])
        logger.info("End quick import %s" %self.name)





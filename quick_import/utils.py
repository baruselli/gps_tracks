from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
import json
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from pprint import pprint
import logging
import traceback
from django.conf import settings

logger = logging.getLogger("gps_tracks")


def do_all_google():
    from download.utils import google_drive_tracks, google_drive_photos, google_photos
    from import_app.utils import import_photos, generate_tracks
    from photos.utils import associate_photos_to_tracks
    logger.info("TracksPhotosImportView do all")
    downloaded_tracks= google_drive_tracks()
    logger.info("downloaded_tracks")
    logger.info(downloaded_tracks)
    generated_tracks= generate_tracks(settings.TRACKS_DIR,files =downloaded_tracks, update=False)
    logger.info("generated_tracks")
    logger.info(generated_tracks)
    downloaded_photos= google_drive_photos()
    downloaded_photos+= google_photos(only_last_year=True)
    logger.info("downloaded_photos")
    logger.info(downloaded_photos)
    imported_photos= import_photos(files=downloaded_photos)
    logger.info("imported_photos")
    logger.info([p.name for p in imported_photos])
    associate_photos_to_tracks(photo_list=imported_photos, track_list=generated_tracks)

def do_all_tomtom():
    from download.utils import download_tomtom
    from import_app.utils import generate_tracks
    logger.info("TracksPhotosImportView do all")
    downloaded_tracks = download_tomtom(ext="csv")
    generated_tracks= generate_tracks(settings.TRACKS_DIR,files = downloaded_tracks, update=False)
    logger.info("generated_tracks")
    logger.info(generated_tracks)

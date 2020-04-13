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
logger = logging.getLogger("gps_tracks")
from django.conf import settings


class DownloadTomtom(View):
    def get(self, request, *args, **kwargs):

        logger.info("DownloadTomtom")

        from .utils import download_tomtom
        download_tomtom(ext="gpx")
        download_tomtom(ext="csv")
        download_tomtom(ext="tcx")
        download_tomtom(ext="kml")
        # gpx
        # logger.info("Download GPX")
        # all_data = base + "/service/webapi/v2/activity/zip/1.zip?format=gpx"
        # r3 = s.get(all_data)
        # out_file = os.path.join(settings.TRACKS_DIR, "tomtom_gpx.zip")
        # open(out_file, "wb").write(r3.content)
        # zip_ref = zipfile.ZipFile(out_file, "r")
        # zip_ref.extractall(os.path.join(settings.TRACKS_DIR, "tomtom"))
        # zip_ref.close()
        # csv
        # logger.info("Download csv")
        # all_data = base + "/service/webapi/v2/activity/zip/1.zip?format=csv"
        # r3 = s.get(all_data)
        # out_file = os.path.join(settings.TRACKS_DIR, "tomtom_csv.zip")
        # open(out_file, "wb").write(r3.content)
        # zip_ref = zipfile.ZipFile(out_file, "r")
        # zip_ref.extractall(os.path.join(settings.TRACKS_DIR, "tomtom"))
        # zip_ref.close()
        # # tcx
        # logger.info("Download tcx")
        # all_data = base + "/service/webapi/v2/activity/zip/1.zip?format=tcx"
        # r3 = s.get(all_data)
        # out_file = os.path.join(settings.TRACKS_DIR, "tomtom_tcx.zip")
        # open(out_file, "wb").write(r3.content)
        # zip_ref = zipfile.ZipFile(out_file, "r")
        # zip_ref.extractall(os.path.join(settings.TRACKS_DIR, "tomtom"))
        # zip_ref.close()
        # logger.info("Download kml")
        # all_data = base + "/service/webapi/v2/activity/zip/1.zip?format=kml"
        # r3 = s.get(all_data)
        # out_file = os.path.join(settings.TRACKS_DIR, "tomtom_kml.zip")
        # open(out_file, "wb").write(r3.content)
        # zip_ref = zipfile.ZipFile(out_file, "r")
        # zip_ref.extractall(os.path.join(settings.TRACKS_DIR, "tomtom"))
        # zip_ref.close()

        message = "Done"
        messages.success(request, message)#
        logger.info(message)

        return redirect(reverse("import"))

class GoogleDriveTracksView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from .utils import google_drive_tracks
        import threading

        logger.info("GoogleDriveTracksView")
        t = threading.Thread(target=google_drive_tracks)
        t.start()

        # generate_tracks(track_dir,ext,update)
        message = "Started import in a parallel thread, check logs for details"
        messages.success(request, message)

        return redirect(reverse("import"))

class GoogleDrivePhotosView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from .utils import google_drive_photos
        import threading

        logger.info("GoogleDrivePhotosView")
        t = threading.Thread(target=google_drive_photos)
        t.start()

        # generate_tracks(track_dir,ext,update)
        message = "Started download in a parallel thread, check logs for details"
        messages.success(request, message)

        return redirect(reverse("import"))

class GooglePhotosView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from .utils import google_photos
        import threading

        logger.info("GooglePhotosView")
        t = threading.Thread(target=google_photos)
        t.start()

        # generate_tracks(track_dir,ext,update)
        message = "Started download in a parallel thread, check logs for details"
        messages.success(request, message)

        return redirect(reverse("import"))




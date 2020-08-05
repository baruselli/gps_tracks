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



class SerializeWaypointsView(View):
    def get(self, request, *args, **kwargs):
        from .utils import serialize
        from tracks.models import Waypoint

        logger.info("SerializeWaypointsView")
        serialize(Waypoint.objects.all(), "waypoints", True)
        message = "OK"
        messages.success(request, message)

        return redirect(reverse("import"))


class SerializeTracksView(View):
    def get(self, request, *args, **kwargs):
        from .utils import serialize
        from tracks.models import Track
        import threading

        logger.info("SerializeTracksView")
        for track in Track.objects.all():
            serialize([track], track.name_wo_path_wo_ext)

        # t = threading.Thread(target=serialize, args = (Track.objects.all(),"tracks",False))
        # t.start()

        # message="Export in a parallel Thread"
        # messages.success(request, message)

        return redirect(reverse("import"))


class SerializePhotosView(View):
    def get(self, request, *args, **kwargs):
        from .utils import serialize
        from tracks.models import Photo
        import threading

        logger.info("SerializePhotosView")

        t = threading.Thread(
            target=serialize, args=(Photo.objects.all(), "photos", True)
        )
        t.start()

        message = "Export in a parallel Thread"
        messages.success(request, message)

        return redirect(reverse("import"))


class SerializeTrackView(View):
    def get(self, request, *args, **kwargs):
        from .utils import serialize
        from tracks.models import Track

        track_id = kwargs.get("track_id", None)
        logger.info("SerializeTrackView %s" %track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)
        serialize([track], track.name_wo_path_wo_ext)

        message = "Done"
        messages.success(request, message)

        return redirect(reverse("track_detail", kwargs={"track_id": track_id}))


class DeserializeView(View):
    def post(self, request, *args, **kwargs):
        from .utils import deserialize
        from tracks.utils import handle_uploaded_files
        from tracks.forms import UploadFileForm
        from django.core.files.storage import FileSystemStorage
        import threading

        from django.contrib import messages
        import os

        logger.info("DeserializeView")
        files = request.FILES.getlist("file")
        from pprint import pprint, pformat
        logger.info(pformat(files))


        if len(files) == 0:
            message = "Please select a file!"
            messages.success(request, message)
            logger.info(message)
            return redirect(reverse("import"))
        elif len(files) == 1:
            f = files[0]
            fs = FileSystemStorage()  # defaults to   MEDIA_ROOT
            filename = fs.save(f.name, f)
            deserialize(os.path.join(settings.MEDIA_ROOT, filename))
            # redirect to processed file
            message = "Deserialized"
            messages.success(request, message)
            logger.info(message)
            return redirect(reverse("import"))
        else:
            # save files to disk
            for f in files:
                fs = FileSystemStorage()  # defaults to   MEDIA_ROOT
                filename = fs.save(f.name, f)
                deserialize(os.path.join(settings.MEDIA_ROOT, filename))
            # process files in parallel thread
            # t = threading.Thread(target=handle_uploaded_files, args = (files,))
            # t.start()
            # generate_tracks(track_dir,ext,update)
            # message="Started import in a parallel thread, check logs for details"
            # messages.success(request, message)
            message = "Deserialized"
            messages.success(request, message)
            logger.info(message)
            return redirect(reverse("import"))

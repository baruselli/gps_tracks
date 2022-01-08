from import_app.utils import get_all_photo_dirs
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
import json
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from pprint import pprint
import logging
import traceback
from waypoints.models import Waypoint
from tracks.models import Track
from photos.models import Photo
from groups.models import Group
from lines.models import Line
from geojson_obj.models import GeoJsonObject
from users.models import User

logger = logging.getLogger("gps_tracks")
from tracks.models import *


class Import(View):

    template_name = "import_app/import.html"

    def get(self, request, *args, **kwargs):

        logger.debug("Import")

        show_timeline=settings.SHOW_GOOGLE_TIMELINE

        n_tracks = Track.objects.count()
        first_track = Track.objects.filter(beginning__isnull=False).order_by("beginning").first()
        last_track = Track.objects.filter(beginning__isnull=False).order_by("beginning").last()
        n_photos = Photo.objects.count()
        first_photo = Photo.objects.filter(time__isnull=False).order_by("time").first()
        last_photo = Photo.objects.filter(time__isnull=False).order_by("time").last()
        n_waypoints = Waypoint.objects.count()
        n_groups = Group.objects.count()
        n_lines = Line.objects.count()
        n_geojson = GeoJsonObject.objects.count()
        n_users = User.objects.count()

        ok_tomtom =  OptionSet.get_option("TOMTOM_USER") and OptionSet.get_option("TOMTOM_PASSWORD")
        ok_garmin =  OptionSet.get_option("GARMIN_USER") and OptionSet.get_option("GARMIN_PASSWORD")
        ok_google =  bool(OptionSet.get_option("GOOGLE_TRACKS_DIRS"))
        from .utils import get_all_photo_dirs
        all_photos_dirs = "; ".join(get_all_photo_dirs())

        from quick_import.models import QuickImport
        quick_imports = QuickImport.objects.all()

        try:
            if settings.DB_TYPE == "postgres":
                from django.db import connection
                cursor = connection.cursor()
                sql = '''
                    SELECT pg_size_pretty( pg_database_size('%s') );
                    ''' % (settings.DB_NAME)
                cursor.execute(sql)
                rows = cursor.fetchall()
                cursor.close()
                db_size = rows[0][0]
            elif settings.DB_TYPE == "sqlite":
                import os
                from humanize import naturalsize
                db_size = naturalsize(os.stat(settings.DB_NAME).st_size)
            else:
                db_size = ""
        except:
            db_site = ""


        return render(request, self.template_name, {
            "show_timeline":show_timeline,
            "n_tracks": n_tracks,
            "first_track":first_track,
            "last_track":last_track,
            "n_photos": n_photos,
            "first_photo":first_photo,
            "last_photo": last_photo,
            "n_waypoints":n_waypoints,
            "n_groups":n_groups,
            "n_lines": n_lines,
            "n_geojson": n_geojson,
            "n_users": n_users,
            "tracks_dir":settings.TRACKS_DIR,
            "photos_dir": settings.PHOTOS_DIR,
            "all_photos_dirs": all_photos_dirs,
            "ok_tomtom":ok_tomtom,
            "ok_garmin":ok_garmin,
            "ok_google": ok_google,
            "quick_imports": quick_imports,
            "db_size":db_size,
        })

class ImportUpdate(View):
    def get(self, request, *args, **kwargs):
        from .utils import generate_tracks

        ext = request.GET.getlist("ext", [])
        import_new_extensions = bool(request.GET.get("import_new_extensions", False))
        update = bool(request.GET.get("update", False))

        import threading
        from django.contrib import messages

        logger.info("ImportUpdate")
        t = threading.Thread(
            target=generate_tracks, args=(settings.TRACKS_DIR, ext, update,import_new_extensions)
        )
        t.start()

        # generate_tracks(track_dir,ext,update)
        message = "Started import in a parallel thread, check logs for details"
        messages.success(request, message)

        return redirect(reverse("import"))


class ImportPhotos(View):
    def get(self, request, *args, **kwargs):
        from .utils import import_photos

        import threading
        from django.contrib import messages

        logger.info("ImportPhotos")
        t = threading.Thread(target=import_photos, kwargs={"update":False})
        t.start()

        message = "Started import in a parallel thread, check logs for details"
        messages.success(request, message)

        return redirect(reverse("import"))

class UpdatePhotos(View):
    def get(self, request, *args, **kwargs):
        from .utils import import_photos

        import threading
        from django.contrib import messages

        logger.info("ImportPhotos")
        t = threading.Thread(target=import_photos, kwargs={"update":True})
        t.start()

        message = "Started import in a parallel thread, check logs for details"
        messages.success(request, message)

        return redirect(reverse("import"))




class UploadTrackView(View):

    # template_name = 'tracks/import.html'

    # def get(self, request,*args, **kwargs):
    #     from .forms import UploadFileForm
    #     form = UploadFileForm()
    #     return redirect(reverse('index'))
    #     return render(request, self.template_name, {"form":form})

    def post(self, request, *args, **kwargs):
        from .utils import handle_uploaded_files, save_uploaded_files
        from .forms import UploadFileForm
        import threading
        from django.contrib import messages

        files = request.FILES.getlist("file")
        logger.info("Upload file(s)")

        if len(files) == 0:
            message = "Please select a file!"
            messages.success(request, message)
            logger.warning("No uploaded files")
            return redirect(reverse("index"))
        elif len(files) == 1:
            f = files[0]
            logger.info("Uploaded one file %s" %f)

            extension = os.path.splitext(f.name)[1]
            if extension in [".gpx", ".csv", ".kml", ".kmz", ".tcx"]:
                type_="track"
            elif extension in [".jpg"]:
                type_="photo"
            else:
                message="Unknown extension %s" %extension
                messages.success(request, message)
                logger.info(message)
                return HttpResponseRedirect(reverse("index") )

            paths = save_uploaded_files(files)

            obj_id = handle_uploaded_files(paths)
            # redirect to processed file
            message = "Imported %s" %type_
            if type_=="track":
                return HttpResponseRedirect(reverse("track_detail", kwargs={"track_id": obj_id}))
            elif type_=="photo":
                return HttpResponseRedirect(reverse("photo_detail", kwargs={"photo_id": obj_id}))
        else:
            # save files to disk
            logger.info("Uploaded many files")
            from pprint import pprint, pformat
            paths = save_uploaded_files(files)
            # process files in parallel thread
            t = threading.Thread(target=handle_uploaded_files, args=(paths,))
            t.start()
            # generate_tracks(track_dir,ext,update)
            message = "Started import in a parallel thread, check logs for details"
            messages.success(request, message)
            return redirect(reverse("index"))

class OtherExtensionsTrackView(View):
    def get(self, request, *args, **kwargs):
        from .utils import generate_tracks_by_prefix

        import threading
        from django.contrib import messages

        track_id = kwargs.get("track_id", None)
        logger.info("OtherExtensionsTrackView %s" %track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        generate_tracks_by_prefix(settings.TRACKS_DIR,track.name_wo_path_wo_ext)


        return HttpResponseRedirect(
                reverse("track_detail", kwargs={"track_id": track_id})
            )

class ReimportTrackView(View):
    def get(self, request, *args, **kwargs):
        track_id = kwargs.get("track_id", None)
        track = get_object_or_404(Track.all_objects, pk=track_id)
        extension = kwargs.get("ext", None)
        from .utils import from_files_to_tracks

        logger.info("Reimport Track %s" %track_id)
        status = track.reimport(extension)

        messages.success(request, status)

        return redirect(reverse("track_detail", args=(track_id,)))

class FailedTracksReimportView(View):
    def get(self, request, *args, **kwargs):

        logger.info("FailedTracksReimportView Track")
        import threading
        from django.contrib import messages
        from .utils import reimport_failed_tracks

        logger.info("ImportUpdate")
        t = threading.Thread(
            target=reimport_failed_tracks
        )
        t.start()

        # generate_tracks(track_dir,ext,update)
        message = "Started import in a parallel thread, check logs for details"
        messages.success(request, message)

        return redirect(reverse("import"))


class DuplicatedFilesView(View):
    template_name = "import_app/duplicated_files.html"
    def get(self, request, *args, **kwargs):

        logger.info("DuplicatedFilesView Track")
        from .utils import find_duplicated_files
        duplicated_files=find_duplicated_files(settings.TRACKS_DIR)

        return render(request, self.template_name, {"duplicated_files":duplicated_files})

class DuplicatedPhotosView(View):
    template_name = "import_app/duplicated_photos.html"
    def get(self, request, *args, **kwargs):

        logger.info("DuplicatedPhotosView Track")
        from .utils import find_duplicated_photos
        duplicated_photos=find_duplicated_photos()

        return render(request, self.template_name, {"duplicated_photos":duplicated_photos})

class DownloadFileView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from tracks.models import Track
        from django.http import HttpResponse
        from wsgiref.util import FileWrapper
        import os

        file_path=request.GET.get("file_path", None)
        from import_app.utils import get_all_photo_dirs
        allowed_dirs = get_all_photo_dirs() + [settings.TRACKS_DIR]

        allowed = False
        if os.path.exists(file_path):
            for dir_ in allowed_dirs:
                if dir_ in file_path:
                    allowed=True

        if allowed:
            wrapper = FileWrapper(open(file_path, "rb"))
            response = HttpResponse(wrapper, content_type="application/force-download")
            out_filename = os.path.basename(file_path).replace(",", "_")
            response["Content-Disposition"] = "filename=" + out_filename
            logger.info(response)
            return response
        else:
            message = "Cannot find file " + file_path
            messages.success(request,message)
            logger.warning(message)
            return redirect(reverse("index"))

class AllFilesReportView(View):
    template_name = "import_app/all_files_report.html"
    def get(self, request, *args, **kwargs):

        logger.info("AllFilesReportView Track")
        from .utils import find_imported_and_existing_files
        all_files=find_imported_and_existing_files()

        return render(request, self.template_name, {"all_files":all_files})

class AllPhotosReportView(View):
    template_name = "import_app/all_photos_report.html"
    def get(self, request, *args, **kwargs):

        logger.info("AllPhotosReportView Track")
        from .utils import find_imported_and_existing_photos
        all_files=find_imported_and_existing_photos()

        return render(request, self.template_name, {"all_files":all_files})


class AllFilesReportJsonView(View):

    def get(self, request, *args, **kwargs):
        from .utils import find_imported_and_existing_files
        return JsonResponse(find_imported_and_existing_files())

class AllPhotosReportJsonView(View):

    def get(self, request, *args, **kwargs):
        from .utils import find_imported_and_existing_photos
        return JsonResponse(find_imported_and_existing_photos())

class ImportNewTracksView(View):
    def get(self, request, *args, **kwargs):
        from .utils import import_new_tracks

        import threading
        from django.contrib import messages

        logger.info("ImportNewTracks")
        logger.info(settings.TRACKS_DIR)
        t = threading.Thread(target=import_new_tracks, args=(str(settings.TRACKS_DIR),))
        t.start()

        message = "Started import in a parallel thread, check logs for details"
        messages.success(request, message)

        return redirect(request.META.get('HTTP_REFERER'))

class ImportNewPhotosView(View):
    def get(self, request, *args, **kwargs):
        from .utils import import_new_photos

        import threading
        from django.contrib import messages

        logger.info("ImportNewPhotos")
        t = threading.Thread(target=import_new_photos)
        t.start()

        message = "Started import in a parallel thread, check logs for details"
        messages.success(request, message)

        return redirect(request.META.get('HTTP_REFERER'))

class GetDirSizesView(View):
    def get(self, request, *args, **kwargs):
        from .utils import get_dir_sizes
        return JsonResponse(get_dir_sizes())

class UploadWaypoints(View):
    """import a gpx consisting of only waypoints"""
    def post(self, request, *args, **kwargs):
        from .utils import handle_uploaded_files, save_uploaded_files
        from .forms import UploadFileForm
        import threading
        from django.contrib import messages

        files = request.FILES.getlist("file")
        logger.info("Upload file(s)")

        if len(files) == 0:
            message = "Please select a file!"
            messages.success(request, message)
            logger.warning("No uploaded files")
            return redirect(reverse("index"))
        else:
            # save files to disk
            logger.info("Uploaded files")
            from pprint import pprint, pformat
            paths = save_uploaded_files(files,gpx_for_waypoints=True)
            # process files in parallel thread
            t = threading.Thread(target=handle_uploaded_files, args=(paths,),kwargs={"gpx_for_waypoints":True})
            t.start()
            # generate_tracks(track_dir,ext,update)
            message = "Started import in a parallel thread, check logs for details"
            messages.success(request, message)
            return redirect(reverse("import"))
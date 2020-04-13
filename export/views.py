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

from tracks.models import Track
from lines.models import Line
from import_app.utils import convert_to_gpx
from django.conf import settings


class LineToGpxView(View):
    def get(self, request, *args, **kwargs):
        import os

        from wsgiref.util import FileWrapper
        from django.http import HttpResponse

        line_id = kwargs.get("line_id", None)
        logger.info("LineToGpxView %s" %line_id)
        line = get_object_or_404(Line, pk=line_id)

        gpx=convert_to_gpx(line.lats,line.long,alts=line.alts)
        out_file = os.path.join(settings.MEDIA_ROOT,line.name+".gpx")
        with open(out_file, 'w') as f:
            f.write(gpx.to_xml())

        wrapper = FileWrapper(open(out_file, "rb"))
        response = HttpResponse(wrapper, content_type="application/force-download")
        out_filename = os.path.basename(out_file).replace(",", "_")
        response["Content-Disposition"] = "filename=" + out_filename
        logger.info(response)
        return response

class LineToKmlView(View):
    def get(self, request, *args, **kwargs):
        from .utils import convert_to_kml
        import os

        from wsgiref.util import FileWrapper
        from django.http import HttpResponse

        line_id = kwargs.get("line_id", None)
        logger.info("LineToKmlView %s" %line_id)
        line = get_object_or_404(Line, pk=line_id)

        kml=convert_to_kml(line.lats,line.long,alts=line.alts)
        out_file = os.path.join(settings.MEDIA_ROOT,line.name+".kml")
        kml.save(out_file)

        wrapper = FileWrapper(open(out_file, "rb"))
        response = HttpResponse(wrapper, content_type="application/force-download")
        out_filename = os.path.basename(out_file).replace(",", "_")
        response["Content-Disposition"] = "filename=" + out_filename
        logger.info(response)
        return response

class TrackToGpxView(View):
    def get(self, request, *args, **kwargs):
        import os

        from wsgiref.util import FileWrapper
        from django.http import HttpResponse

        track_id = kwargs.get("track_id", None)
        logger.info("TrackToGpxView %s" %track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        gpx=convert_to_gpx(track.td.lats,track.td.long,alts=track.td.alts,times=track.td.times)
        out_file = os.path.join(settings.MEDIA_ROOT,track.name_wo_path_wo_ext+"_exported.gpx")
        with open(out_file, 'w') as f:
            f.write(gpx.to_xml())

        wrapper = FileWrapper(open(out_file, "rb"))
        response = HttpResponse(wrapper, content_type="application/force-download")
        out_filename = os.path.basename(out_file).replace(",", "_")
        response["Content-Disposition"] = "filename=" + out_filename
        logger.info(response)
        return response

class TrackToKmlView(View):
    def get(self, request, *args, **kwargs):
        from .utils import convert_to_kml
        import os

        from wsgiref.util import FileWrapper
        from django.http import HttpResponse

        track_id = kwargs.get("track_id", None)
        logger.info("TrackToKmlView %s" %track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        kml=convert_to_kml(track.td.lats,track.td.long,alts=track.td.alts,times=track.td.times)
        out_file = os.path.join(settings.MEDIA_ROOT,track.name_wo_path_wo_ext+"_exported.kml")
        kml.save(out_file)

        wrapper = FileWrapper(open(out_file, "rb"))
        response = HttpResponse(wrapper, content_type="application/force-download")
        out_filename = os.path.basename(out_file).replace(",", "_")
        response["Content-Disposition"] = "filename=" + out_filename
        logger.info(response)
        return response

class SmoothedTrackToGpxView(View):
    def get(self, request, *args, **kwargs):
        import os

        from wsgiref.util import FileWrapper
        from django.http import HttpResponse

        track_id = kwargs.get("track_id", None)
        logger.info("SmoothedTrackToGpxView %s" %track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        gpx=convert_to_gpx(track.td.lats_smooth3,track.td.long_smooth3,
                        alts=track.td.alts_smooth3,times=track.td.times_smooth3)
        out_file = os.path.join(settings.MEDIA_ROOT,track.name_wo_path_wo_ext+"_smoothed.gpx")
        with open(out_file, 'w') as f:
            f.write(gpx.to_xml())

        wrapper = FileWrapper(open(out_file, "rb"))
        response = HttpResponse(wrapper, content_type="application/force-download")
        out_filename = os.path.basename(out_file).replace(",", "_")
        response["Content-Disposition"] = "filename=" + out_filename
        logger.info(response)
        return response

class SmoothedTrackToKmlView(View):
    def get(self, request, *args, **kwargs):
        from .utils import convert_to_kml
        import os

        from wsgiref.util import FileWrapper
        from django.http import HttpResponse

        track_id = kwargs.get("track_id", None)
        logger.info("SmoothedTrackToKmlView %s" %track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        kml=convert_to_kml(track.td.lats_smooth3,track.td.long_smooth3,
                        alts=track.td.alts_smooth3,times=track.td.times_smooth3)
        out_file = os.path.join(settings.MEDIA_ROOT,track.name_wo_path_wo_ext+"_smoothed.kml")
        kml.save(out_file)

        wrapper = FileWrapper(open(out_file, "rb"))
        response = HttpResponse(wrapper, content_type="application/force-download")
        out_filename = os.path.basename(out_file).replace(",", "_")
        response["Content-Disposition"] = "filename=" + out_filename
        logger.info(response)
        return response

class FilesFromTracks(View):
    # create new files with a single track each
    def get(self, request, *args, **kwargs):
        from tracks.models import Track
        import os

        out_track_list = []
        track_id = kwargs.get("track_id", None)
        track = get_object_or_404(Track.all_objects, pk=track_id)
        logger.info("FilesFromTracks %s" % track.pk)


        out_dir = os.path.join(settings.MULTITRACK_ROOT, track.name_wo_path_wo_ext)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_file_base = os.path.join(out_dir, track.name_wo_path_wo_ext)

        # kml/kmz
        if track.kml or track.kmz:
            track.info("Writing files with a single track: kml/kmz")

            try:
                from fastkml import kml
                from .utils import get_all_nodes
                k = kml.KML()
                if track.kml:
                    k.from_string(track.kml.encode('utf8'))
                elif track.kmz:
                    k.from_string(track.kmz.encode('utf8'))
                track.info("Reading points")
                main_folder = list(k.features())[0]
                track.info("Main folder: %s %s " % (main_folder.name, main_folder))
                folders = list(main_folder.features())[0]
                all_folders = [n for n in get_all_nodes(main_folder, "features") if n.__class__.__name__ == "Folder"]
                track.info("All folders: %s" % ([f.name for f in all_folders]))
                all_placemarks = [n for n in get_all_nodes(main_folder, "features") if
                                  n.__class__.__name__ == "Placemark"]
                tracks = [p for p in all_placemarks if
                          p.geometry.__class__.__name__ in ["MultiLineString", "LineString"]]
                waypoints = [p for p in all_placemarks if p.geometry.__class__.__name__ == "Point"]

                # for each track I create a kml object with a folder in which I put the track
                for i, t in enumerate(sorted(tracks, key=lambda x: x.name)):
                    out_file = out_file_base + "_(" + str(i) + ")_" + t.name + ".kml"
                    track.info("Write %s" % out_file)
                    # k_new=k
                    k_new = kml.KML()
                    new_doc = kml.Document(k.ns, 'did', 'd name', 'd description')
                    k_new.append(new_doc)
                    new_folder = kml.Folder(k.ns, 'fid', 'f name', 'f description')
                    new_doc.append(new_folder)
                    new_folder.append(t)
                    # k_new._features=[new_folder,]
                    # new_folder._features=[t,]
                    # main_folder=list(k_new.features())[0]
                    # main_folder._features=[new_folder,]
                    with open(out_file, 'w') as f:
                        f.write(k_new.to_string(prettyprint=True))
                    out_track_list.append(out_file)
                    del (k_new)

            except Exception as e:
                track.error(e)

        # TODO: kml with gx

        # gpx
        if track.gpx_file:
            try:
                import gpxpy
                track.info("Writing files with a single track: gpx")
                _gpx = gpxpy.parse(open(track.gpx_file, "r"))
                tracks = _gpx.tracks
                track.info("Tracks: %s" % tracks)
                for i, t in enumerate(sorted(tracks, key=lambda x: x.name)):
                    out_file = out_file_base + "_(" + str(i) + ")_" + t.description + ".gpx"
                    track.info("Write %s" % out_file)
                    _gpx_temp = _gpx
                    _gpx_temp.tracks = [t, ]  # I substitute the whole list with a single track
                    import os
                    with open(out_file, 'w') as f:
                        f.write(_gpx_temp.to_xml())
                    out_track_list.append(out_file)
                    del (_gpx_temp)

            except Exception as e:
                track.error(e)

        from pprint import pformat
        message = "Created files: %s" % pformat(out_track_list)

        messages.success(request, message)

        #        return redirect(reverse("track_detail",args=(track_id,)))
        return None

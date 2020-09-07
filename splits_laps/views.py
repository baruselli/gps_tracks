from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from tracks.models import *
import json
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from pprint import pprint
import logging
import traceback
logger = logging.getLogger("gps_tracks")

from waypoints.models import Waypoint
from tracks.models import Track
from photos.models import Photo
from groups.models import Group
from tracks.utils import get_colors, pace_from_speed
from tracks.models import Track
from lines.models import Line
from lines.utils import create_line


# Create your views here.


class FindLapsView(View):
    template_name = "splits_laps/track_laps.html"

    def get(self, request, *args, **kwargs):
        track_id = kwargs.get("track_id", None)
        logger.info("FindLapsView %s" % track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        # print(track)

        from .utils import track_slices, stats_from_slices
        from .forms import FindLapsForm
        form = FindLapsForm()

        import datetime  # used in the saved json
        try:
            laps=eval(track.td.laps)
        except Exception as e:
            logger.error("Cannot get laps: %s" %e)
            #print (track.td.laps)
            laps=[]
        try:
            import json
            stats=json.loads(track.td.laps_stats)
        except Exception as e:
            logger.error("Cannot get stats laps: %s" %e)
            print(track.td.laps_stats)
            stats={}

        # if track.td.laps_indices:
        #     laps = track_slices(track, track.td.laps_indices)
        #     stats = stats_from_slices(laps)
        # else:
        #     laps = []
        #     stats = []

        reduce_points = request.GET.get('reduce_points', 'every')
        # print(reduce_points)

        return render(
            request,
            self.template_name,
            {
                "track": track,
                "form": form,
                "laps": laps,
                "stats": stats,
                "request": request.GET.urlencode(),
                "reduce_points": reduce_points
            },
        )

    def post(self, request, *args, **kwargs):
        from .forms import FindLapsForm
        form = FindLapsForm(request.POST)

        track_id = kwargs.get("track_id", None)
        logger.info("FindLapsView post %s" % track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)
        reduce_points = request.GET.get('reduce_points', 'every')

        if form.is_valid():
            starting_lon = form.cleaned_data['starting_lon']
            starting_lat = form.cleaned_data['starting_lat']
            time_threshold = form.cleaned_data['time_threshold']
            space_threshold = form.cleaned_data['space_threshold']
            min_laps = form.cleaned_data['min_laps']
            max_laps = form.cleaned_data['max_laps']
            threshold_length = form.cleaned_data['threshold_length']
            back_forth = form.cleaned_data['back_forth']

            if starting_lon and starting_lat:
                initial_point = [starting_lat, starting_lon]
            else:
                initial_point = None

            from .utils import find_laps, stats_from_slices

            result = find_laps(
                track=track,
                time_threshold=time_threshold,
                space_threshold=space_threshold,
                initial_point=initial_point,
                threshold_length=threshold_length,
                min_laps=min_laps,
                max_laps=max_laps,
                back_forth=back_forth,

            )

            message = result["message"]
            laps = result["laps"]
            indices = result["indices"]
            stats = stats_from_slices(laps)


            from splits_laps.utils import get_reduced_slices
            try:
                track.info("Setting laps_stats and laps")
                import json
                track.td.laps_stats = json.dumps(stats)
                reduced_laps= get_reduced_slices(laps)
                track.td.laps = str(reduced_laps)
                track.save()
                track.td.save()
            except Exception as e:
                track.warning("Cannot set laps: %s" % e)

            track.td.laps_indices = indices
            track.n_laps = len(laps) - 2  # exclude before and after
            track.save()
            track.td.save()
            track.set_json_LD()

            colors = get_colors(len(result))

            return render(request, self.template_name, {"form": form,
                                                        "track": track,
                                                        "message": message,
                                                        "laps": laps,
                                                        "stats": stats,
                                                        "reduce_points": reduce_points
                                                        }
                          )
        else:
            return render(request, self.template_name, {"form": form, "has_error": True})

class SplitsView(View):
    template_name = "splits_laps/track_splits.html"

    def get(self, request, *args, **kwargs):
        track_id = kwargs.get("track_id", None)
        logger.info("SplitsView %s" % track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        from .utils import track_slices, stats_from_slices

        if track.td.split_indices:
            splits = track_slices(track, track.td.split_indices, add_before_after=False, name="Split")
            stats = stats_from_slices(splits)
        else:
            track.info("Cannot read splits")
            splits = []
            stats = []

        from .forms import TrackSplitsForm
        form = TrackSplitsForm(instance=track)

        reduce_points = request.GET.get('reduce_points', 'every')
        return render(
            request,
            self.template_name,
            {
                "track": track,
                "splits": splits,
                "stats_splits": stats,
                "request": request.GET.urlencode(),
                "reduce_points": reduce_points,
                "form": form
            },
        )

    def post(self, request, *args, **kwargs):
        from .forms import TrackSplitsForm

        track_id = kwargs.get("track_id", None)
        logger.info("TrackView post %s" %track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        form = TrackSplitsForm(request.POST or None, instance=track)

        if form.is_valid():
            track = form.save()

            track.info("Set splits_km by form at %s" %track.splits_km)
            if True:
                track.get_split_indices()
                track.set_splits()
                track.set_json_LD()

            request_get= request.GET.urlencode()

            return HttpResponseRedirect(
                reverse("splits", kwargs={"track_id": track_id})+ "?" + request_get
            )
        else:
            return render(
                request, self.template_name, {"form": form, "has_error": True}
            )



# class GetSplitsView(View):
#     def get(self, request, *args, **kwargs):
#         track_id = kwargs.get("track_id", None)
#         logger.info("GetSplitsView %s" % track_id)
#         track = get_object_or_404(Track.all_objects, pk=track_id)

#         try:
#             n_km = float(request.GET.get("n_km", 1))
#         except:
#             n_km = 1

#         from .forms import TrackSplitsForm
#         form = TrackSplitsForm(instance=track)

#         track.get_split_indices()

#         reduce_points = request.GET.get('reduce_points', 'every')

#         return redirect(reverse("splits", args=(track_id,)) + "?reduce_points=" + reduce_points)

class DeleteSplitsView(View):
    def get(self, request, *args, **kwargs):
        track_id = kwargs.get("track_id", None)
        logger.info("DeleteSplitsView %s" % track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        request = request.GET.urlencode()
        track.td.split_indices = [0]
        track.td.save()

        return redirect(reverse("splits", args=(track_id,)) + "?" + request)

class DeleteLapsView(View):
    def get(self, request, *args, **kwargs):
        track_id = kwargs.get("track_id", None)
        logger.info("DeleteLapsView %s" % track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        request = request.GET.urlencode()

        track.td.laps_indices = [0]
        track.td.save()
        track.set_json_LD()
        track.td.laps_stats = ""
        track.td.laps = ""
        track.save()
        track.td.save()

        return redirect(reverse("find_laps", args=(track_id,)) + "?" + request)


class LapToLineView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages

        track_id = kwargs.get("track_id", None)
        track = get_object_or_404(Track.all_objects, pk=track_id)
        lap = int(request.GET.get("lap", 1))
        every = int(request.GET.get("every", 1))

        logger.info("lap %s" %lap)
        logger.info("every %s" % every)
        logger.info("LapToLineView %s" % track.pk)

        indices=track.td.laps_indices
        indices.insert(0, 0)  # insert first point
        indices.append(track.n_points)  # and last

        #print(indices,len(indices))
        index_start=indices[lap]
        index_end =indices[lap+1]
        lats=track.td.lats[index_start:index_end+1:every]
        long = track.td.long[index_start:index_end:every]
        alts = track.td.alts[index_start:index_end:every]

        #readd initial point to make circuit close
        if lats:
            lats.append(lats[0])
            long.append(long[0])
            alts.append(alts[0])

        line, created = create_line(lats, long, alts,
                                    track.name_wo_path_wo_ext+"_lap"+str(lap))
        line.line_type = "path"
        line.color = "brown"
        line.track = track
        line.closed=True
        line.save()

        return redirect(reverse("line_detail", args=(line.pk,)))

class SegmentsView(View):
    template_name = "splits_laps/track_segments.html"

    def get(self, request, *args, **kwargs):
        track_id = kwargs.get("track_id", None)
        logger.info("SplitsView %s" % track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        reduce_points = request.GET.get('reduce_points', 'every')
        return render(
            request,
            self.template_name,
            {
                "track": track,
                "request": request.GET.urlencode(),
                "reduce_points": reduce_points
            },
        )

class SubtracksView(View):
    template_name = "splits_laps/track_subtracks.html"

    def get(self, request, *args, **kwargs):
        track_id = kwargs.get("track_id", None)
        logger.info("SplitsView %s" % track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)
        subtrack_names=track.get_subtrack_names()
        use_points = int(request.GET.get('use_points', 0))

        reduce_points = request.GET.get('reduce_points', 'every')
        return render(
            request,
            self.template_name,
            {
                "track": track,
                "request": request.GET.urlencode(),
                "reduce_points": reduce_points,
                "subtrack_names":subtrack_names,
                "use_points":use_points,
            },
        )
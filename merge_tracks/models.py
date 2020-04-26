from django.db import models
import json
from logger.models import Log
from django.urls import reverse
import logging
logger = logging.getLogger("gps_tracks")
from tracks.models import Track, TrackDetail
from waypoints.models import Waypoint
from groups.models import Group
from photos.models import Photo


class MergedTrack(models.Model):
    """
    Object that keep tracks of how tracks should be merged into one
    """
    name = models.CharField(max_length=512, verbose_name="Name", null=False, blank=False, unique=True)
    output_track = models.OneToOneField(Track,null=True,on_delete=models.CASCADE, related_name="output_track")
    input_tracks = models.ManyToManyField(Track,blank=False, related_name="input_tracks")
    delete_original_tracks = models.BooleanField(default=False, verbose_name="Hide input tracks")
    gpx_files = models.TextField(verbose_name="File gpx", null=True, blank=True, unique=False)
    kml_files = models.TextField(verbose_name="File kml", null=True, blank=True, unique=False)
    kmz_files = models.TextField(verbose_name="File kmz", null=True, blank=True, unique=False)
    csv_files = models.TextField(verbose_name="File csv", null=True, blank=True, unique=False)
    tcx_files = models.TextField(verbose_name="File tcx", null=True, blank=True, unique=False)
    modified = models.DateTimeField(auto_now=True, verbose_name="Date of modification", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Date of creation", null=True, blank=True)
    input_tracks_names = models.TextField(null=True, blank=True, unique=False)
    order = models.TextField(verbose_name="Priority {track_pk1:order1,track_pk2:order2}", null=True, blank=True, unique=False, default="{}")

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def merge_tracks(self):
        if self.input_tracks(manager="all_objects").all():
            tracks_q=self.input_tracks(manager="all_objects").filter(is_merged=False) #cannot merge tracks already merged
        else:
            return None
        name=self.name

        import json
        self.input_tracks_names=json.dumps([t.name_wo_path_wo_ext for t in tracks_q])
        self.save()

        manual_sort = False
        if self.order and self.order!="{}":
            try:
                logger.info("Manual ordering")
                # try to read the dict given in frontend
                order_dict = eval(self.order)
                # if some pks are missing, put them at the end
                input_pks = tracks_q.order_by("beginning").values_list("pk",flat=True)
                max_order = max(order_dict.values())
                for pk in input_pks:
                    if pk not in order_dict:
                       order_dict[pk]=max_order
                       max_order+=1
                # create list with ordered tracks
                tracks=[]
                for w in sorted(order_dict, key=order_dict.get, reverse=False):
                    track=Track.all_objects.get(pk=int(w))
                    logger.info("Adding track %s with priority %s" %(track,order_dict[w]))
                    tracks.append(track)
            
                manual_sort=True # successful manual sorting!
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error("Cannot read order: %s. Order by beginning time." %e)

        if not manual_sort:
            tracks=tracks_q.order_by("beginning")

        logger.info("Merging tracks %s" %tracks)

        # todo later
        n_points=0
        for t in tracks:
            n_points+=t.n_points


        if self.output_track:
            track=self.output_track
        else:
            q=Track.objects.filter(name_wo_path_wo_ext=name)

            # track name already existing, I do not overwrite!
            if q:
                return
            else:
                track = Track(name_wo_path_wo_ext=name)
                track.save()
                self.output_track=track
                self.save()

        if not (track.log):
            track.log = Log.objects.create(pk=track.pk)
            track.info("Log created!")
            track.save()
        if not (track.td):
            if track.log:
                track.info("Creating track detail")
            track.td = TrackDetail.objects.create(pk=track.pk)
            track.save()
        logger.info("%s" %track)
        track.n_points=n_points #todo later
        track.is_merged=True
        track.save()

        tracks_ids=[]
        for t in tracks:
            track.merged_tracks.add(t)
            tracks_ids.append(t.pk)
            #todo: add gpx, csv files

            track.user=t.user
        track.save()

        ## check which points to add for each track, to avoid overlaps
        # in case of overlap, I give precedence to the first track
        indices_tracks=[]
        cases=[]
        import bisect
        dict_cases={
            0: "all for first track",
            1: "all after the previous ones",
            2: "all before the previous ones",
            3: "partly after the previous ones",
            4: "partly before the previous ones",
            5: "partly before and after the previous ones",
            6: "nothing",
            -1: "error"
        }
        for i,t in enumerate(tracks):
            case=-1
            times=t.td.times
            logger.info("%s: beginning %s, end %s" %(t, times[0],times[-1]))
            # first track, keep all
            if i==0:
                # for the first track I keep everything
                initial_t = times[0]
                final_t = times[-1]
                indices_track=[],[0,-1]
                case=0
            else:
                # print(initial_t,times[0],final_t,times[-1])
                ## case 1: track is completely after the previous ones
                if times[0]>=final_t:
                    # add nothing before, and all after
                    indices_track=[],[0,-1]
                    final_t = times[-1]
                    case=1
                ## case 2: track is completely before the previous one
                elif times[-1]<=initial_t:
                    # add all before, and nothing after
                    indices_track=[0,-1],[]
                    initial_t = times[0]
                    case=2
                ## case 3: track is partly after the previous ones
                elif initial_t<=times[0]<=final_t<=times[-1]:
                    # add nothing before, and something after
                    final_index = bisect.bisect_left(times, final_t)
                    indices_track=[],[final_index,-1]
                    final_t = times[-1]
                    case=3
                ## case 4: track is partly before the previous ones
                elif times[0]<=initial_t<=times[-1]<=final_t:
                    # add something before, and nothing after
                    initial_index = bisect.bisect_right(times, initial_t)
                    indices_track=[0,initial_index],[]
                    initial_t = times[0]
                    case=4
                ## case 5: track comprises the previous ones
                elif times[0]<=initial_t<=final_t<=times[-1]:
                    # add something before and after
                    initial_index = bisect.bisect_right(times, initial_t)
                    final_index = bisect.bisect_left(times, final_t)
                    indices_track=[0,initial_index],[final_index,-1]
                    initial_t = times[0]
                    final_t = times[-1]
                    case=5
                ##  case 6: track is comprised inside the previous one
                else:
                    ## add nothing
                    indices_track=[],[]
                    case=6

            cases.append(case)
            indices_tracks.append(indices_track) 
            logger.info("Added indices for track %s, %s: %s"%(t, dict_cases[case],indices_track))


        for f_name in track.td.array_fields_1+track.td.array_fields_2:
            f_name=f_name[1:]
            setattr(track.td, f_name, []) #reset
            for t,indices in zip(tracks, indices_tracks):
                new_value = getattr(t.td, f_name, [])
                if not new_value:
                    new_value=[None for i in range(t.n_points)]
                track.info("Adding %s from %s, indices %s" %(f_name,t.name_wo_path_wo_ext,indices))
                old_value = getattr(track.td, f_name, [])
                ## indices to add before
                if indices[0]:
                    setattr(track.td, f_name,  new_value[indices[0][0]:indices[0][1]] + old_value  )
                ## indices to add after
                if indices[1]:
                    setattr(track.td, f_name,  old_value + new_value[indices[1][0]:indices[1][1]]  )

        track.n_points=len(track.td.lats) #todo later

        # segment and subtrack indices
        # this only works if i put tracks one after the other (cases 0, 1)
        track.td.subtrack_indices=[]
        track.td.segment_indices=[]
        initial_point_number=0
        if not 2 in cases and not 3 in cases and not 4 in cases and not 5 in cases and not 6 in cases and not -1 in cases:
            for t in tracks:
                # print(t, t.td.subtrack_indices,t.td.segment_indices)
                if not t.td.subtrack_indices:
                    t.td.subtrack_indices=[0]
                    t.save()
                if not t.td.segment_indices:
                    t.td.segment_indices=[0]
                    t.save()
                track.td.subtrack_indices+=[i + initial_point_number for i in t.td.subtrack_indices]  # index of first point in subtrack
                track.td.segment_indices+=[i + initial_point_number for i in t.td.segment_indices]   # index of first point in segment
                initial_point_number += t.n_points

        #print(track, track.td.subtrack_indices, track.td.segment_indices)

        track.n_tracks = len(track.td.subtrack_indices)
        track.n_segments = len(track.td.segment_indices)

        track.save()
        track.td.save()

        track.has_freq=any([t.has_freq for t in tracks])
        track.has_hr=any([t.has_hr for t in tracks])
        track.save()

        track.set_heartrate_freq()

        track.set_all_properties()

        for wp in Waypoint.objects.filter(track_pk__in=tracks_ids):
            track.info("Adding wp %s under waypoints2" %wp)
            wp.track2=track
            wp.save()

        #photos
        for p in Photo.objects.filter(tracks__in=tracks_ids):
            track.info("Adding photo %s" %p)
            track.photos.add(p)

        for g in Group.objects.filter(tracks__in=tracks_ids):
            track.info("Adding group %s" %g)
            g.tracks.add(track)
            g.save()


        # remove old tracks from manual groups
        for t in tracks:
            for g in t.groups.filter(is_path_group=False):
                t.groups.remove(g)

        if self.delete_original_tracks:
            for t in tracks:
                t.is_active=False
                t.save()
                # print(t,t.is_active)
        else:
            for t in tracks:
                t.is_active=True
                t.save()

        # files, original tracks
        # substitute old tracks in groups?
        # wayoint.track2

        return track

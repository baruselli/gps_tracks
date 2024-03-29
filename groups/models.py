from django.db import models
from django.contrib.postgres.fields import ArrayField
import json

from django.urls import reverse
import logging
from pprint import pprint
from photos.models import Photo
from options.models import OptionSet

logger = logging.getLogger("gps_tracks")

class Group(models.Model):

    size = models.IntegerField(null=True, blank=True, default=0)
    number = models.IntegerField(null=True, blank=True, unique=True)
    name = models.CharField(max_length=255, verbose_name="Name", null=False, blank=False,unique=True)
    color = models.CharField(max_length=255, verbose_name="Color", null=True, blank=True)
    avg_lat = models.FloatField(null=True)
    avg_long = models.FloatField(null=True)
    min_lat = models.FloatField(null=True)
    min_long = models.FloatField(null=True)
    max_lat = models.FloatField(null=True)
    max_long = models.FloatField(null=True)
    tracks = models.ManyToManyField("tracks.Track",blank=True)
    modified = models.DateTimeField(auto_now=True, verbose_name="Date of modification", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Date of creation", null=True, blank=True)
    exclude_from_search = models.BooleanField(default=False, verbose_name="Exclude tracks from distance and similarities queries")
    properties_json = models.TextField(verbose_name="Json with properties of all tracks", null=True, blank=True, unique=False,default="{}")
    auto_update_properties = models.BooleanField(default=False,verbose_name="Auto update properties for scatter plots")
    modified = models.DateTimeField(auto_now=True, verbose_name="Date of modification", null=True, blank=True)
    min_date = models.DateField(null=True)
    max_date = models.DateField(null=True)
    has_freq = models.BooleanField(default=False)
    has_hr = models.BooleanField(default=False)
    has_times = models.BooleanField(default=True)
    has_alts = models.BooleanField(default=True)
    use_points_instead_of_lines = models.BooleanField(default=False)
    is_path_group = models.BooleanField(default=False)
    hide_in_forms = models.BooleanField(default=False, verbose_name="Hide from track form")
    always_use_lines = models.BooleanField(default=False, verbose_name="Always use lines instead of points in this page")
    rules = models.ManyToManyField('groups.GroupRule',blank=True)
    rules_act_as_and = models.BooleanField(default=True, verbose_name="Take intersection of rules (instead of union)")
    tracks_priority = models.IntegerField(blank=True, null=True, verbose_name="Default priority to assign to tracks")

    @property
    def n_tracks(self):
        return self.tracks.count()

    def get_properties(self):
        import json
        self.check_json()
        # from pprint import pprint
        # pprint(json.loads(self.properties_json))
        return json.loads(self.properties_json)

    def check_properties(self,properties=None):
        """check if the saved json has the right tracks"""
        if properties is None:
            properties=self.get_properties()
        import time
        start = time.time()
        stored_tracks_names =set([t["name"] for t in properties["Tracks"]])
        real_tracks_names = set(self.tracks.all().values_list("name_wo_path_wo_ext",flat=True))

        missing_tracks=real_tracks_names-stored_tracks_names
        excess_tracks=stored_tracks_names-real_tracks_names
        end=time.time()

        logger.info("Time for calling check_properties: %s" %(end-start))

        properties["warnings"]={
           "missing_tracks":list(missing_tracks),
           "excess_tracks":list(excess_tracks),
        }

        return properties

    def set_attributes(self,updated_tracks=[],refresh_all=False):
        import time
        start = time.time()

        import numpy as np
        logger.info("Set_attributes %s" %self)
        logger.info("updated_tracks %s" %str(updated_tracks))
        self.size= self.tracks.count()
        try:
            logger.info("Avg quantities")
            self.min_lat =  np.nanmin([x for x in self.tracks.all().values_list("min_lat", flat=True) if x is not None])
            self.min_long = np.nanmin([x for x in self.tracks.all().values_list("min_long", flat=True) if x is not None])
            self.max_lat =  np.nanmax([x for x in self.tracks.all().values_list("max_lat", flat=True) if x is not None])
            self.max_long = np.nanmax([x for x in self.tracks.all().values_list("max_long", flat=True) if x is not None])
            self.avg_lat =  np.nanmean([x for x in self.tracks.all().values_list("avg_lat", flat=True) if x is not None])
            self.avg_long = np.nanmean([x for x in self.tracks.all().values_list("avg_long", flat=True) if x is not None])
            self.min_date = np.nanmin([x for x in self.tracks.all().values_list("date", flat=True) if x is not None])
            self.max_date = np.nanmax([x for x in self.tracks.all().values_list("date", flat=True) if x is not None])
            # self.avg_lat = np.nanmean(self.tracks.all().values_list("avg_lat", flat=True))
            # self.avg_long = np.nanmean(self.tracks.all().values_list("avg_long", flat=True))
            # self.min_lat = np.nanmin(self.tracks.all().values_list("min_lat", flat=True))
            # self.min_long = np.nanmin(self.tracks.all().values_list("min_long", flat=True))
            # self.max_lat = np.nanmax(self.tracks.all().values_list("max_lat", flat=True))
            # self.max_long = np.nanmax(self.tracks.all().values_list("max_long", flat=True))
            # self.min_date = np.nanmin(self.tracks.all().values_list("date", flat=True))
            # self.max_date = np.nanmax(self.tracks.all().values_list("date", flat=True))
            self.has_freq = np.any(self.tracks.all().values_list("has_freq", flat=True))
            self.has_hr = np.any(self.tracks.all().values_list("has_hr", flat=True))
            self.has_times = np.any(self.tracks.all().values_list("has_times", flat=True))
            self.has_alts = np.any(self.tracks.all().values_list("has_alts", flat=True))

            #tracks
            from json_views.utils import tracks_json, add_ranks, add_colors_to_json, add_numbers_to_json,fix_geometries_json
            import json
            logger.info("properties_json %s" % self)
            use_lines = self.n_tracks<OptionSet.get_option("MAX_N_TRACKS_AS_LINES") or self.always_use_lines
            if use_lines:
                points_line="MultiLineString"
                reduce_points="smooth2"
            else:
                points_line="Point"
                reduce_points="single"

            try:
                old_json=json.loads(self.properties_json)
            except:
                old_json={}
            # if group is new, or I decide to refresh all: I take the json of all tracks
            if refresh_all or not json or not "Tracks" in old_json:
                logger.info("Refreshing all, %s, %s" %(points_line,reduce_points))
                json_obj = tracks_json( tracks=self.tracks.all(),
                                        with_color=True,
                                        points_line=points_line,
                                        reduce_points=reduce_points,
                                        add_flat=True,
                                        ranks=True,
                                        group_pk=self.pk,
                                        keep_empty_set=True)


            # if I am updating: I only take new tracks or updated tracks
            else:
                # find tracks not in json
                old_tracks_names =set([t["name"] for t in old_json["Tracks"]])
                current_tracks_names = set(self.tracks.all().values_list("name_wo_path_wo_ext",flat=True))
                new_tracks_names = current_tracks_names-old_tracks_names
                removed_tracks_names =  old_tracks_names - current_tracks_names
                logger.info ("new_tracks_names %s" %new_tracks_names)
                logger.info ("removed_tracks_names %s" %removed_tracks_names)
                # take updated tracks form input
                from tracks.models import Track
                updated_tracks_in_group=Track.objects.filter(name_wo_path_wo_ext__in=updated_tracks).filter(groups__id=self.pk)
                new_tracks_in_group = Track.objects.filter(name_wo_path_wo_ext__in=new_tracks_names)
                # build json for new/updated tracks
                tracks_to_get_json=(updated_tracks_in_group|new_tracks_in_group).distinct()
                json_obj = tracks_json(tracks=tracks_to_get_json,
                                       with_color=True,
                                       points_line=points_line,
                                       reduce_points=reduce_points,
                                       add_flat=True,
                                       ranks=False, # I add ranks later
                                       #group_pk=self.pk,
                                       keep_empty_set=True)
                new_tracks = json_obj["Tracks"]
                # add old tracks, if not already in the new json, or removed
                new_json=[]
                new_track_names_list=[]
                for a in json_obj["Tracks"]+old_json["Tracks"]: #first the new object, so I keep updated infos
                    if a["name"] not in removed_tracks_names and a["name"] not in new_track_names_list:
                        new_track_names_list.append(a["name"])
                        new_json.append(a)
                # add ranks
                new_tracks_ok, grades, colors_legend, details_legend = add_ranks(new_json)
                # add colors
                new_tracks_ok = add_colors_to_json(new_tracks_ok)
                # add progressive number
                new_tracks_ok=add_numbers_to_json(new_tracks_ok)
                # set geometry type according to tracks number
                new_tracks_ok = fix_geometries_json(new_tracks_ok, use_lines=use_lines)
                # build new json
                new_json={}
                new_json["Tracks"]=new_tracks_ok
                new_json["grades"]=grades
                new_json["colors_legend"]=colors_legend
                new_json["details_legend"]=details_legend
                # recalculate bounds
                new_json["minmaxlatlong"] = [
                                                min(old_json["minmaxlatlong"][0],json_obj["minmaxlatlong"][0]),
                                                max(old_json["minmaxlatlong"][1], json_obj["minmaxlatlong"][1]),
                                                min(old_json["minmaxlatlong"][2], json_obj["minmaxlatlong"][2]),
                                                max(old_json["minmaxlatlong"][3], json_obj["minmaxlatlong"][3]),
                                             ]
                json_obj = new_json

            feats_dict={
                "has_freq":int(self.has_freq),
                "has_hr": int(self.has_hr),
                "has_times": int(self.has_times),
                "has_alts": int(self.has_alts),
            }
            if not "features" in json_obj:
                json_obj["features"]=feats_dict
            else:
                json_obj["features"].update(feats_dict)

            from django.core.serializers.json import DjangoJSONEncoder
            self.properties_json=json.dumps(json_obj,cls=DjangoJSONEncoder)
            self.save()
            #print(self.properties_json)
        except:
            import traceback
            traceback.print_exc()

        self.save()
        end = time.time()
        logger.info("End set_attributes %s"  %(end-start))
        return self.properties_json

    def check_json(self):
        """checks if the saved json contains all tracks"""
        logger.info("check_json")
        import time
        start = time.time()
        import json
        p = json.loads(self.properties_json)

        if p:
            track_names=set([t["name"] for t in p["Tracks"]])
            track_names_all = set(self.tracks.all().values_list("name_wo_path_wo_ext",flat=True))

        if not p or track_names!=track_names_all:
            if not p:
                logger.info("No saved JSON")
            else:
                logger.info("Tracks in excess: %s" %(track_names-track_names_all))
                logger.info("Missing tracks: %s" % (track_names_all - track_names))
            self.set_attributes()

        end = time.time()
        logger.info("OK check_json %s " %(end-start))
        return

    def get_statistics(self):
        """return best and worst track for each feature, plus averages"""
        from tracks.utils import get_options, format_feature
        options = get_options()
        group_dict = {}

        # from pprint import pprint
        # pprint(json.loads(group.properties_json)["Tracks"])

        properties_dict = {}
        tracks_json = json.loads(self.properties_json)["Tracks"]

        for ok, ov in options.items():
            if "feature_rank" in ov.keys(): # and ok=="Heartrate":
                tracks_json_feature = [t for t in tracks_json if t[ov["feature_name"]] and t[ov["feature_rank"]]]
                n_tracks_feature = len(tracks_json_feature)
                tracks_json_feature.sort(key=lambda x: x[ov["feature_rank"]])
                tracks_list=[]

                n_best_tracks=OptionSet.get_option("N_BEST_TRACKS_GROUP")
                if n_tracks_feature>n_best_tracks:
                    tracks_to_include = list(range(1,n_best_tracks+1))+list(range(n_tracks_feature-n_best_tracks+1,n_tracks_feature+1))
                else:
                    tracks_to_include = range(1,n_tracks_feature+1)

                for t in tracks_json_feature:
                    if t[ov["feature_rank"]] in tracks_to_include:
                        formatted_value = format_feature(t[ov["feature_name"]], ok)
                        track_dict={"link": t["link"],
                                    "name": t["name"],
                                    "raw_value": t[ov["feature_name"]],
                                    "rank": t[ov["feature_rank"]],
                                    "date": t["date"],
                                    "value":formatted_value}
                        tracks_list.append(track_dict)

                import numpy as np
                average = np.nanmean([t[ov["feature_name"]] for t in tracks_json_feature])
                average = format_feature(average,ok)

                if "has_total" in ov and ov["has_total"]:
                    total = np.nansum([t[ov["feature_name"]] for t in tracks_json_feature])
                    total = format_feature(total,ok)
                else:
                    total = None

                group_dict[ok]={"tracks":tracks_list,
                                "average": average,
                                "total": total}

        return group_dict

    class Meta:
        verbose_name = "Group"
        ordering = ["pk"]
        #app_label = "tracks"

    def __unicode__(self):
        return "Group " + str(self.name)

    def __repr__(self):
        return "Group " + str(self.name)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        super(Group, self).save(*args, **kwargs)
        self.assign_priority_to_tracks()

    def filtered_tracks(self,initial_queryset=None):
        """
        filter tracks according to assigned rules
        """
        logger.info("filtered_tracks for group %s" %self)
        from tracks.models import Track 

        if initial_queryset:
            tracks=initial_queryset
        else:
            tracks=Track.all_objects.all()

        if self.rules.all():
            if self.rules_act_as_and:
                # rules go in AND
                total_tracks= Track.all_objects.all()
                for rule in self.rules.all():
                    logger.info("applying rule %s in AND" %rule)
                    #print("tracks in group",tracks)
                    tracks_rule = rule.filtered_tracks(tracks)
                    logger.info("tracks_rule %s" %tracks_rule.count())
                    # intersection with what is there; this is the safest way to do intersection
                    total_tracks = total_tracks.filter(pk__in=tracks_rule.values("pk")) 
                    logger.info("total_tracks %s"  %total_tracks.count())
                logger.info("OK filtered_tracks for group %s" %self)
                return total_tracks
            else:
                # rules go in OR
                total_tracks = Track.objects.none()
                all_pks=[]
                for rule in self.rules.all():
                    logger.info("applying rule %s in OR" %rule)
                    tracks_rule = rule.filtered_tracks(tracks)
                    logger.info("tracks_rule %s" %tracks_rule.count())
                    all_pks.extend(tracks_rule.values_list("pk",flat=True))
                    #total_tracks = total_tracks | tracks_rule  #union -> gives problem if a queryset has the "distance" field
                    #logger.info("total_tracks %s"  %total_tracks.count())
                total_tracks=Track.all_objects.filter(pk__in=all_pks)
                logger.info("OK filtered_tracks for group %s" %self)
                return total_tracks
        else:
            logger.info("OK filtered_tracks for group %s" %self)
            return Track.objects.none()

    def get_infos_on_filtered_tracks(self):

        filtered_tracks=self.filtered_tracks()

        filtered_tracks_not_in_group=filtered_tracks.exclude(pk__in=self.tracks.all().values("pk"))

        tracks_in_group_not_filtered=self.tracks.all().exclude(pk__in=filtered_tracks.values("pk"))

        tracks_in_group_filtered=self.tracks.all().filter(pk__in=filtered_tracks.values("pk"))

        return{
            "filtered_tracks_not_in_group":filtered_tracks_not_in_group.count(),
            "filtered_tracks_not_in_group_pk":"_".join([str(a) for a in filtered_tracks_not_in_group.values_list("pk",flat=True)]),
            "tracks_in_group_not_filtered":tracks_in_group_not_filtered.count(),
            "tracks_in_group_not_filtered_pk":"_".join([str(a) for a in tracks_in_group_not_filtered.values_list("pk",flat=True)]),
            "tracks_in_group_filtered":tracks_in_group_filtered.count(),
            "tracks_in_group_filtered_pk":"_".join([str(a) for a in tracks_in_group_filtered.values_list("pk",flat=True)]),
        }

    def add_tracks_from_rules(self):
        tracks_to_add_pk=self.get_infos_on_filtered_tracks()["filtered_tracks_not_in_group_pk"]
        if tracks_to_add_pk:
            tracks_pk=[int(a) for a in tracks_to_add_pk.split("_")]

            from tracks.models import Track
            tracks=Track.objects.filter(pk__in=tracks_pk)
            names=[]
            tracks_list=[]
            for track in tracks:
                self.tracks.add(track)
                logger.info("Added track %s to group %s" %(track,self))
                names.append(track.name_wo_path_wo_ext)
                tracks_list.append(track) #set_attributes requires list

            self.set_attributes(updated_tracks=tracks_list)

            return names      

    def assign_priority_to_tracks(self):
        from django.db.models import Q
        # I update track priority either to modify the default value 5, or to increase it
        if self.tracks_priority is not None:
            self.tracks.filter(Q(priority=5)|Q(priority__lt=self.tracks_priority)).update(priority = self.tracks_priority)


class GroupRule(models.Model):
    name = models.CharField(max_length=255, verbose_name="Name", null=False, blank=False,unique=True)
    query_string = models.TextField(null=True, blank=True, unique=False,default="?")

    def __str__(self):
        return self.name

    def filter_dict(self):
        """
        returns a dict to mimic a request.GET dict obtained in a view 
        """
        from urllib import parse
        try:
            return_dict_with_lists = parse.parse_qs(parse.urlsplit(self.query_string).query)
            # for some stupid reason parse_qs always returns lists
            return_dict = {a:b[0] for a, b in return_dict_with_lists.items()}

            if not return_dict:
                return_dict = {"no_search":1}
            return return_dict
        except:
            return {"no_search":1}

    def request_string(self):
        """
        returns a string, starting with ?, to be appended to the url
        """
        query_string = self.query_string
        try:
            if query_string.startswith("?"):
                return query_string
            else:
                return "?"+query_string
        except:
            return "?no_query=1"
        #import urllib
        #return urllib.parse.urlencode(self.filter_dict())

    def filtered_tracks(self,initial_queryset=None):
        """
        filters tracks according to the mimicked request.GET dict
        """
        from tracks.utils import filter_tracks
        #print("initial_queryset",initial_queryset)
        return filter_tracks(request=self.filter_dict(),initial_queryset=initial_queryset)
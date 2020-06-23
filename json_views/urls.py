from django.conf.urls import url
from . import views

urlpatterns = [
    ### groups
    url(r"^all_groups/$", views.GroupsJsonView.as_view(), name="allgroups_json"),
    url(r"^group/properties/(?P<group_id>[0-9]+)/$", views.GroupPlotsJsonView.as_view(), name="group_json_properties", ),
    url(r"^group/stats/(?P<group_id>[0-9]+)/$", views.GroupStatisticsJsonView.as_view(), name="group_json_statistics", ),
    ### wps
    url(r"^all_waypoints/$", views.WaypointsJsonView.as_view(), name="allwps_json"),
    ### photos
    url(r"^all_photos/$", views.PhotosJsonView.as_view(), name="allphotos_json"),
    ### line(s)
    url(r"^all_lines/$", views.LinesJsonView.as_view(), name="alllines_json"),
    url(r"^line/(?P<line_id>[0-9]+)/$", views.LineJsonView.as_view(), name="line_json"),
    ### geojson
    url(r"^geojson/(?P<geojsonobj_id>[0-9]+)/", views.GeoJsonObjectJsonView.as_view(), name="geojsonobj_json", ),
    url(r"^geojson/all/", views.GeoJsonObjectsJsonView.as_view(), name="geojsonobj_json_all", ),
    ### tracks
    ## one
    url(r"^track/json_list_of_points/(?P<track_id>[0-9]+)/$", (views.TrackJsonView.as_view()), name="track_json_list_of_points", ),
    url(r"^track/json_splits/(?P<track_id>[0-9]+)/$", (views.TrackJsonSplitsView.as_view()), name="track_json_splits", ),
    url(r"^track/json_laps/(?P<track_id>[0-9]+)/$", (views.TrackJsonLapsView.as_view()), name="track_json_laps", ),
    url(r"^track/json_segments/(?P<track_id>[0-9]+)/$", (views.TrackJsonSegmentsView.as_view()), name="track_json_segments", ),
    url(r"^track/json_subtracks/(?P<track_id>[0-9]+)/$", (views.TrackJsonSubtracksView.as_view()), name="track_json_subtracks", ),
    #url(r"^track/jsonDL/(?P<track_id>[0-9]+)/$", (views.TrackJsonDLView.as_view()), name="track_json_DL", ),
    #url(r"^track/json_smooth/(?P<track_id>[0-9]+)/$", (views.TrackJsonSmoothView.as_view()),name="track_json_smooth",),
    #many
    url(r"^tracks/as_lines", views.TracksAsLinesJsonView.as_view(), name="tracks_as_lines_json"),
    url(r"^tracks/as_point_lists", views.TracksAsPointListsJsonView.as_view(), name="tracks_as_point_lists_json", ),
    url(r"^tracks/alts", views.TracksAltsJsonView.as_view(), name="tracks_alts_json"),
]

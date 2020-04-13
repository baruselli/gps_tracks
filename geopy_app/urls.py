from django.conf.urls import url
from . import views

# from models import *
# from djgeojson.views import GeoJSONLayerView
from . import models
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView

urlpatterns = [
    #track(s)
    url(r"^tracks/$", views.TrackGeopyView.as_view(), name="geopy_tracks"),
    url(r"^track/(?P<track_id>[0-9]+)/$", views.SingleTrackGeopyView.as_view(), name="geopy_track", ),
    #photo(s)
    url(r"^photos/$", views.PhotoGeopyView.as_view(), name="geopy_photos"),
    url(r"^photo/(?P<track_id>[0-9]+)/$", views.SinglePhotoGeopyView.as_view(), name="geopy_photo", ),
    #waypoint(s)
    url(r"^waypoints/$", views.WaypointGeopyView.as_view(), name="geopy_waypoints"),
    url(r"^waypoint/(?P<waypoint_id>[0-9]+)/$", views.SingleWaypointGeopyView.as_view(), name="geopy_waypoint", ),
    #line(s)
    url(r"^lines/$", views.LineGeopyView.as_view(), name="geopy_lines"),
    url(r"^line/(?P<line_id>[0-9]+)/$", views.SingleLineGeopyView.as_view(), name="geopy_line", ),
    url(r"^line/(?P<line_id>[0-9]+)/get_alts/$", views.GetLineAltsView.as_view(), name="alts_line", ),
]
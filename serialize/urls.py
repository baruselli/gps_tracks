from django.conf.urls import url
from . import views


urlpatterns = [
    url(r"^track/(?P<track_id>[0-9]+)/$",views.SerializeTrackView.as_view(),name="serialize_track",),
    url(r"^deserialize$", views.DeserializeView.as_view(), name="deserialize"),
    url(r"^tracks$", views.SerializeTracksView.as_view(),name="serialize_tracks",),
    url(r"^waypoints$",views.SerializeWaypointsView.as_view(),name="serialize_waypoints",),
    url(r"^photos$", views.SerializePhotosView.as_view(), name="serialize_photos", ),
]


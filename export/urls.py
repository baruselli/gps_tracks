from django.conf.urls import url
from . import views


urlpatterns = [
        #line export
        url(r"^line/(?P<line_id>[0-9]+)/gpx_convert/$", views.LineToGpxView.as_view(), name="gpx_line", ),
        url(r"^line/(?P<line_id>[0-9]+)/kml_convert/$", views.LineToKmlView.as_view(), name="kml_line", ),
        #track export
        url(r"^track/(?P<track_id>[0-9]+)/gpx_convert/$", views.TrackToGpxView.as_view(), name="track_to_gpx", ),
        url(r"^track/(?P<track_id>[0-9]+)/kml_convert/$", views.TrackToKmlView.as_view(), name="track_to_kml", ),
        url(r"^track/(?P<track_id>[0-9]+)/gpx_convert_smooth/$", views.SmoothedTrackToGpxView.as_view(),name="smoothed_track_to_gpx", ),
        url(r"^track/(?P<track_id>[0-9]+)/kml_convert_smooth/$", views.SmoothedTrackToKmlView.as_view(),name="smoothed_track_to_kml", ),
        url(r"^track/(?P<track_id>[0-9]+)/files_from_tracks/$", views.FilesFromTracks.as_view(),name="files_from_tracks", ),
]
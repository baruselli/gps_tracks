from django.conf.urls import url
from . import views

# from models import *
# from djgeojson.views import GeoJSONLayerView
from . import models
from django.views.decorators.cache import cache_page

urlpatterns = [

    # many tracks
    url(r"^main$", views.TrackListGeneralView.as_view(), name="track_gen_index"),
    url(r"^tracks_list$", views.TracksListView.as_view(), name="track_index"),
    url(r"^tracks_map$", views.TracksMapView.as_view(), name="tracks_map"),
    url(r"^tracks_set_all_properties/$",views.TracksSetAllPropertiesView.as_view(),name="tracks_set_all_properties",),


    # single track
    url(r"^track/(?P<track_id>[0-9]+)/$", views.TrackView.as_view(), name="track_detail"),
    url(r"^track/plot_test/(?P<track_id>[0-9]+)/$",views.TrackPlotTestView.as_view(),name="track_plot_test",),
    url(r"^track/source/(?P<ext>[a-z]+)/(?P<track_id>[0-9]+)/$", views.TrackSourceView.as_view(), name="track_source", ),
    url(r"^track/download/(?P<ext>[a-z]+)/(?P<track_id>[0-9]+)/$",views.DownloadSourceView.as_view(),name="download_source",),
    url(r"^track/(?P<track_id>[0-9]+)/photos/$",views.TrackPhotosView.as_view(),name="track_photos_detail",),
    url(r"^track/plots/(?P<track_id>[0-9]+)/$",views.TrackStatisticsView.as_view(),name="track_statistics",),
    url(r"^track/smooth/(?P<track_id>[0-9]+)/$",views.TrackSmoothView.as_view(),name="track_smooth",),
    url(r"^track/rolling/(?P<track_id>[0-9]+)/$",views.TrackRollingView.as_view(),name="rolling_track",),
    url(r"^track/track_set_all_properties/(?P<track_id>[0-9]+)/$",views.TrackSetAllPropertiesView.as_view(),name="track_set_all_properties",),

    url(r"^track/subtrack/(?P<track_id>[0-9]+)/(?P<subtrack_number>[0-9]+)$",views.SubTrackView.as_view(),name="subtrack",),


    # delete
    url(r"^import/tracks/delete$", views.DeleteTracks.as_view(), name="delete_tracks"),
    url(r"^import/track/delete/(?P<track_id>[0-9]+)$",views.DeleteTrack.as_view(),name="delete_track",),
    url(r"^import/track/delete_file/(?P<track_id>[0-9]+)$",views.DeleteTrackAndFile.as_view(),name="delete_file",),
    url(r"^import/track/delete_empty",views.DeleteEmptyTracks.as_view(),name="delete_empty_tracks",),

    #url(r"^import/similarities", views.SimilaritiesView.as_view(), name="find_similarities"),
    # url(r"^track/(?P<track_id>[0-9]+)/edit/$",views.EditTrackView.as_view(),name="edit_track",),
    #  url(r"^track/(?P<track_id>[0-9]+)/similar_tracks/$",views.SimilarTracksView.as_view(),name="similar_tracks",),

    ##autocomplete
    url(r'^track-autocomplete/$',views.TrackAutocomplete.as_view(),name='track-autocomplete', ),
    url(r'^track_all-autocomplete/$',views.TrackAllAutocomplete.as_view(),name='track_all-autocomplete', ),
    url(r'^track-autocompletename/$',views.TrackAutocompleteName.as_view(),name='track-autocompletename', ),
]


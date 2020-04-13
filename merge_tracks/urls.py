from django.conf.urls import url
from . import views

urlpatterns = [
    #index
    url(r"^merged_track/main$", views.MergedTracksListView.as_view(), name="merged_tracks_index"),
    #single obj
    url(r"^merged_track/(?P<id>[0-9]+)/$", views.MergedTrackView.as_view(), name="merged_track"),
    url(r"^merged_track/create/$", views.CreateMergedTrackView.as_view(), name="create_merged_track", ),
    url(r"^merged_track/modify/(?P<id>[0-9]+)/$", views.CreateMergedTrackView.as_view(),name="edit_merged_track", ),
    url(r"^merged_track/delete/(?P<id>[0-9]+)$", views.DeleteMergedTrackView.as_view(), name="delete_merged_track", ),
    url(r"^merged_track/reimport/(?P<id>[0-9]+)/$", views.ReimportMergedTrackView.as_view(),name="reimport_merged_track", ),
]
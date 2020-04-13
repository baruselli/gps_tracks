from django.conf.urls import url
from . import views

urlpatterns = [
    #main
    url(r"^main$", views.BlacklistListView.as_view(), name="index_blacklist", ),
    #single
    url(r"^blacklist/(?P<blo_id>[0-9]+)/$", views.BlacklistObjView.as_view(), name="blacklist_obj", ),
    url(r"^blacklist/delete/(?P<blo_id>[0-9]+)/$", views.DeleteBlo.as_view(), name="delete_blo", ),
    url(r"^blacklist/", views.BlacklistObjView.as_view(), name="new_blo", ),
    #delete track
    url(r"^delete_track/(?P<track_id>[0-9]+)$", views.DeleteTrackAndBlacklist.as_view(),name="delete_track_bl", ),

]
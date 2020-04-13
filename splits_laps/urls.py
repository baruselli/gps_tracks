from django.conf.urls import url
from . import views


urlpatterns = [
    #laps
    url(r"^find_laps/(?P<track_id>[0-9]+)/$", views.FindLapsView.as_view(), name="find_laps", ),
    url(r"^find_laps/create_line/(?P<track_id>[0-9]+)/$", views.LapToLineView.as_view(), name="lap_to_line", ),
    url(r"^delete_splits/(?P<track_id>[0-9]+)/$", views.DeleteSplitsView.as_view(), name="delete_splits", ),
    #splits
    url(r"^splits/(?P<track_id>[0-9]+)/$", views.SplitsView.as_view(), name="splits", ),
    url(r"^delete_lap/(?P<track_id>[0-9]+)/delete/$", views.DeleteLapsView.as_view(), name="delete_laps", ),
    #url(r"^get_splits/(?P<track_id>[0-9]+)/$", views.GetSplitsView.as_view(), name="get_splits", ),
    #segments
    url(r"^segments/(?P<track_id>[0-9]+)/$", views.SegmentsView.as_view(), name="segments", ),
    # subtracks
    url(r"^subtracks/(?P<track_id>[0-9]+)/$", views.SubtracksView.as_view(), name="subtracks", ),

]
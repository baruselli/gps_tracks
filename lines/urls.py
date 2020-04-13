from django.conf.urls import url
from . import views

urlpatterns = [
    #main
    url(r"^main", views.LineListView.as_view(), name="line_index"),
    #all
    url(r"^delete$", views.DeleteLinesView.as_view(), name="delete_lines"),
    url(r"^map$", views.AllLinesView.as_view(), name="lines_map"),
    #single
    url(r"^line/(?P<line_id>[0-9]+)/$", views.LineView.as_view(), name="line_detail", ),
    url(r"^line/modify/(?P<line_id>[0-9]+)/$", views.CreateLineView.as_view(), name="create_line", ),
    url(r"^line/delete/(?P<line_id>[0-9]+)/$", views.DeleteLineView.as_view(), name="delete_line", ),
    #draw
    url(r"^draw$", views.CreateLineView.as_view(), name="create_line"),
    #from line
    url(r"^track_to_line/(?P<track_id>[0-9]+)/$", views.TrackToLineView.as_view(), name="track_to_line", ),
]
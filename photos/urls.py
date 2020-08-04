from django.conf.urls import url
from . import views

# from models import *
# from djgeojson.views import GeoJSONLayerView
from . import models
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView

urlpatterns = [
    #index
    url(r"^main$", views.PhotosListGeneralView.as_view(), name="photo_gen_index"),
    url(r"^photos_show", views.PhotosShowView.as_view(), name="photos_show"),
    # url(r"^main", views.PhotoListView.as_view(), name="photo_index"),
    # all photos
    url(r"^delete$", views.DeletePhotos.as_view(), name="delete_photos"),
    # single photo
    url(r"^photo/(?P<photo_id>[0-9]+)/$", views.PhotoView.as_view(), name="photo_detail"),
    url(r"^delete_photo/(?P<photo_id>[0-9]+)/$", views.DeletePhotoView.as_view(), name="delete_photo"),
    # url(r"^photo/modify/(?P<id>[0-9]+)/$", views.EditPhotoView.as_view(), name="edit_photo", ),
    # link photos to tracks
    url(r"^link$", views.LinkPhotos.as_view(), name="link_photos"),
    url(r"^link_track/(?P<track_id>[0-9]+)/$", views.LinkPhotosTrackView.as_view(), name="link_photos_track", ),
    #autocomplete
    url(r'^photo-autocomplete/$',views.PhotoAutocomplete.as_view(),name='photo-autocomplete', ),

]
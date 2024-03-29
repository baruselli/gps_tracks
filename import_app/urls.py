from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^main/$", views.Import.as_view(), name="import"),
    #tracks import
    # url(r"^gpx/import$", views.ImportUpdate.as_view(), {"ext": [".gpx"], "update": False}, name="import_gpx", ),
    # url(r"^gpx/update$", views.ImportUpdate.as_view(), {"ext": [".gpx"], "update": True}, name="update_gpx", ),
    # url(r"^kml/import$", views.ImportUpdate.as_view(), {"ext": [".kml"], "update": False}, name="import_kml", ),
    # url(r"^kml/update$", views.ImportUpdate.as_view(), {"ext": [".kml"], "update": True}, name="update_kml", ),
    # url(r"^kmz/import$", views.ImportUpdate.as_view(), {"ext": [".kmz"], "update": False}, name="import_kmz", ),
    # url(r"^kmz/update$", views.ImportUpdate.as_view(), {"ext": [".kmz"], "update": True}, name="update_kmz", ),
    # url(r"^csv/import$", views.ImportUpdate.as_view(), {"ext": [".csv"], "update": False}, name="import_csv", ),
    # url(r"^csv/update$", views.ImportUpdate.as_view(), {"ext": [".csv"], "update": True}, name="update_csv", ),
    # url(r"^tcx/import$", views.ImportUpdate.as_view(), {"ext": [".tcx"], "update": False}, name="import_tcx", ),
    # url(r"^tcx/update$", views.ImportUpdate.as_view(), {"ext": [".tcx"], "update": True}, name="update_tcx", ),
    url(r"^import_update_tracks$", views.ImportUpdate.as_view(), name="import_update_tracks", ),
    # wrong tracks
    url(r"^failed_tracks_reimport/$", views.FailedTracksReimportView.as_view(), name="failed_tracks_reimport", ),
    # list of duplicated file tracks tracks
    url(r"^duplicated_files/$", views.DuplicatedFilesView.as_view(), name="duplicated_files", ),
    url(r"^duplicated_photos/$", views.DuplicatedPhotosView.as_view(), name="duplicated_photos", ),
    # download a single file
    url(r"^download_file/$", views.DownloadFileView.as_view(), name="download_file", ),
    # 1 track import
    url(r"^track_import/(?P<track_id>[0-9]+)/other_extensions/$", views.OtherExtensionsTrackView.as_view(),name="track_other_extensions", ),
    url(r"^track_reimport/(?P<track_id>[0-9]+)/(?P<ext>[a-z]+)/$", views.ReimportTrackView.as_view(),name="reimport_track", ),
    url(r"^upload$", views.UploadTrackView.as_view(), name="upload_track"),
    url(r"^all_files_report$", views.AllFilesReportView.as_view(), name="all_files_report"),
    url(r"^all_files_report_json$", views.AllFilesReportJsonView.as_view(), name="all_files_report_json"),
    url(r"^import_new_tracks$", views.ImportNewTracksView.as_view(), name="import_new_tracks"),
    # photos
    url(r"^photos/import$", views.ImportPhotos.as_view(), name="import_photos"),
    url(r"^photos/update$", views.UpdatePhotos.as_view(), name="update_photos"),
    url(r"^all_photos_report$", views.AllPhotosReportView.as_view(), name="all_photos_report"),
    url(r"^all_photos_report_json$", views.AllPhotosReportJsonView.as_view(), name="all_photos_report_json"),
    url(r"^import_new_photos$", views.ImportNewPhotosView.as_view(), name="import_new_photos"),
    # dir infos
    url(r"^get_dir_sizes$", views.GetDirSizesView.as_view(), name="get_dir_sizes"),
    # waypoints
    url(r"^waypoints/upload$", views.UploadWaypoints.as_view(), name="upload_waypoints"),

]

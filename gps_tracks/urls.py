"""gps_tracks URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from .utils import match_url_path

urlpatterns = [
                url(r"^admin/", admin.site.urls),
                url(r'accounts/', include('django.contrib.auth.urls')),
                url(r"", include("base.urls")),
                url(r"tracks/", include("tracks.urls")),
                url(r"googletimeline/", include("googletimeline.urls")),
                url(r"export/", include("export.urls")),
                url(r"import/", include("import_app.urls")),
                url(r"serialize/", include("serialize.urls")),
                url(r"download/", include("download.urls")),
                url(r"geopy/", include("geopy_app.urls")),
                url(r"help/", include("help_app.urls")),
                url(r"quick_import/", include("quick_import.urls")),
                url(r"geojson_obj/", include("geojson_obj.urls")),
                url(r"lines/", include("lines.urls")),
                url(r"photos/", include("photos.urls")),
                url(r"users/", include("users.urls")),
                url(r"groups/", include("groups.urls")),
                url(r"waypoints/", include("waypoints.urls")),
                url(r"blacklists/", include("blacklists.urls")),
                url(r"splits_laps/", include("splits_laps.urls")),
                url(r"many_tracks_/", include("many_tracks.urls")),
                url(r"logger/", include("logger.urls")),
                url(r"options/", include("options.urls")),
                url(r"json/", include("json_views.urls")),
                url(r"merge_tracks/", include("merge_tracks.urls")),
] 

static_media = static(match_url_path(settings.MEDIA_BASE_DIR), document_root=settings.MEDIA_BASE_DIR)
urlpatterns+=static_media
print(settings.MEDIA_BASE_DIR, static_media)

# add additional urls for other photo dirs
for additional_photo_dir in settings.ADDITIONAL_PHOTO_DIRS:
    new_url = static(match_url_path(additional_photo_dir), document_root=additional_photo_dir)
    urlpatterns += new_url
    print(additional_photo_dir, new_url)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        # path('__debug__/', include(debug_toolbar.urls)),
        # For django versions before 2.0:
        url(r"^__debug__/", include(debug_toolbar.urls))
    ] + urlpatterns

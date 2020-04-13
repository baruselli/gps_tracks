from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
import json
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from pprint import pprint
import logging
import traceback
logger = logging.getLogger("gps_tracks")
from tracks.models import Group

class GoogleHistorySeleniumView(View):
    def get(self, request, *args, **kwargs):

        from googletimeline.utils import googlehistoryselenium

        import threading
        from django.contrib import messages

        logger.info("GoogleHistorySeleniumView")
        t = threading.Thread(target=googlehistoryselenium, args=())
        t.start()

        message = "Started import in a parallel thread, check logs for details"
        messages.success(request, message)

        return redirect(reverse("import"))

class GoogleHistoryFilesView(View):
    template_name = "googletimeline/history_files.html"
    def get(self, request, *args, **kwargs):
        logger.info("GoogleHistoryFilesView")

        from .utils import get_history_files

        files=get_history_files()

        q=Group.objects.filter(name="Google timeline")
        if q:
            group_pk=q[0].pk
        else:
            group_pk=None


        return render(
            request,
            self.template_name,
            {
                "files": files,
                "group_pk":group_pk
            },
        )

class ImportGoogleHistoryFilesView(View):
    def get(self, request, *args, **kwargs):
        logger.info("ImportGoogleHistoryFilesView")

        from .utils import get_history_files
        from django.conf import settings
        import os
        files=get_history_files(find_in_db=False)
        files_ok=[os.path.join(settings.TRACKS_DIR,"timeline",f["file"]+f["extension"]) for f in files if f["file"] ]

        import threading
        from import_app.utils import  generate_tracks
        t = threading.Thread(
            target=generate_tracks, args=(settings.TRACKS_DIR, [".kml"], False, files_ok)
        )
        t.start()


        message = "Started import in a parallel thread, check logs for details"
        messages.success(request, message)
        return redirect(reverse("import"))



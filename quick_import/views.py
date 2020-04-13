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
from django.conf import settings

logger = logging.getLogger("gps_tracks")


class TracksPhotosImportView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages

        import threading
        from quick_import.utils import do_all_google
        t = threading.Thread(target=do_all_google)
        t.start()

        # generate_tracks(track_dir,ext,update)
        message = "Started import in a parallel thread, check logs for details"
        messages.success(request, message)

        return redirect(reverse("index"))

class QuickImportTomtomView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages

        import threading
        from quick_import.utils import do_all_tomtom
        t = threading.Thread(target=do_all_tomtom)
        t.start()

        message = "Started import in a parallel thread, check logs for details"
        messages.success(request, message)

        return redirect(reverse("index"))
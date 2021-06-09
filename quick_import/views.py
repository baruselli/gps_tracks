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


class QuickImportExecuteView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from .models import QuickImport
        import threading
        id = kwargs.get("id", None)
        quick_import = QuickImport.objects.get(pk=id)
        t = threading.Thread(target=quick_import.execute)
        t.start()

        message = "Started import in a parallel thread, check logs for details"
        messages.success(request, message)

        return redirect(reverse("index"))

from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from tracks.models import *
import json
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from pprint import pprint
import logging
import traceback
logger = logging.getLogger("gps_tracks")

from waypoints.models import Waypoint
from tracks.models import Track
from photos.models import Photo
from groups.models import Group
from blacklists.models import Blacklist


class TrackLogView(View):
    template_name = "logger/track_log.html"

    def get(self, request, *args, **kwargs):
        track_id = kwargs.get("track_id", None)
        logger.debug("TrackLogView %s" % track_id)
        track = get_object_or_404(Track.all_objects, pk=track_id)

        return render(
            request,
            self.template_name,
            {
                "track": track,
                "request": request.GET.urlencode()
            },
        )

class LogsView(View):
    template_name = "logger/logs.html"

    def get(self, request, *args, **kwargs):
        logger.debug("LogsView")

        from django.conf import settings
        logs_dir = settings.LOGS_DIR
        import glob, os
        import datetime
        os.chdir(logs_dir)
        print(logs_dir)

        files=[]
        for file in glob.glob("*.log"):
            try:
                file_dict={}
                file_dict["file"]=file
                file_dict["name"]=file[:-4]
                file_dict["date"]=datetime.datetime.strptime(file[0:8],"%Y%m%d")
                file_dict["level"]=file[9:-4]
                file_dict["size"]=os.path.getsize(file)
                files.append(file_dict)
            except:
                pass

        files.sort(key = lambda x:x["date"],reverse=False)

        return render(
            request,
            self.template_name,
            {
                "files":files
            },
        )

class LogView(View):
    template_name = "logger/logs_file.html"

    def get(self, request, *args, **kwargs):

        import os
        file_name = request.GET.get("name")+".log"

        file_path = os.path.join(settings.LOGS_DIR, file_name)
        logger.debug("LogDebugView %s" %file_path)
        data_file = open(file_path , 'r',encoding="utf-8")

        import pandas as pd
        df = pd.read_csv(file_path,sep="\t",header=None, names=['Level', 'Time',"File","Method","Line","Message"])


        context = {'file': df.to_html(index=False,border = 0, justify="left"),'title':"Log %s" %file_name}

        return render(
            request,
            self.template_name,
            context
        )

class DownloadLogView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from django.http import HttpResponse
        from wsgiref.util import FileWrapper
        import os

        name = request.GET.get("name")+".log"

        file_path=os.path.join(settings.LOGS_DIR,name)
        print(file_path)
        logger.info("DownloadSourceView %s" % file_path)
        if os.path.exists(file_path):
            wrapper = FileWrapper(open(file_path, "rb"))
            response = HttpResponse(wrapper, content_type="application/force-download")
            out_filename = os.path.basename(file_path).replace(",", "_")
            response["Content-Disposition"] = "filename=" + out_filename
            logger.info(response)
            return response
        else:
            message = "Cannot find file " + file_path
            messages.success(message)
            logger.warning(message)
            return redirect(reverse("logs", track_id=track_id))


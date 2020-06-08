from django.http import  HttpResponseRedirect
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


class HelpView(View):
    template_name = "help_app/help.html"
    def get(self, request, *args, **kwargs):
        logger.debug("HelpView")
        return render(request, self.template_name,)

class AboutView(View):
    template_name = "help_app/about.html"
    def get(self, request, *args, **kwargs):
        logger.debug("AboutView")
        return render(request, self.template_name,)
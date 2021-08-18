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
from .models import QuickImport

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

class QuickImportEditView(View):
    template_name = "quick_import/quick_import_edit.html"
    def get(self, request, *args, **kwargs):
        id = kwargs.get("id", None)

        print(request.GET)

        logger.debug("QuickImportEditView")
        Model=QuickImport

        if id:
            from .forms import QuickImportForm as ModelForm
            object = Model.objects.get(pk=id)
            form = ModelForm(instance=object )

            return render(
                request,
                self.template_name,
                {"obj": object, "id": id, "form": form},
            )
        else:
            
            from .forms import QuickImportForm as ModelForm
            form = ModelForm()
            return render(
                request, self.template_name, {"form": form, "id": id}
            )

    def post(self, request, *args, **kwargs):
        from .models import QuickImport as Model

        id = kwargs.get("id", None)

        if id:
            from .forms import QuickImportForm as ModelForm
            instance = get_object_or_404(Model, pk=id)
            form = ModelForm(request.POST or None, instance=instance)
            new = False
            logger.info("Modify object %s" % id)
        else:
            from .forms import QuickImportForm as ModelForm
            form = ModelForm(request.POST)
            new = True
            logger.info("Create object")

        if form.is_valid():
            f = form.save()
            id = f.pk
            instance = get_object_or_404(Model, pk=id)
            logger.info("Object pk %s" % f.pk)

            instance.save()

            messages.success(request, "OK")

            return HttpResponseRedirect(
                reverse("import")
            )
        else:
            logger.error("Form")
            return render(
                request, self.template_name, {"form": form, "has_error": True}
            )

class QuickImportDeleteView(View):

    def get(self, request, *args, **kwargs):

        id = kwargs.get("id", None)

        logger.debug("QuickImportDeleteView")


        obj = QuickImport.objects.get(pk=id)
        obj.delete()

        message = "Quick Import %s deleted" %obj
        messages.success(request, message)

        return HttpResponseRedirect(
            reverse("import")
        )

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

from .models import *
from tracks.utils import get_colors
from tracks.models import *
from waypoints.models import *

class GroupListView(View):

    template_name = "groups/group_index.html"

    def get(self, request, *args, **kwargs):
        logger.debug("GroupListView")
        groups = Group.objects.all()
        colors = get_colors(len(groups))
        for g,c in zip(groups,colors):
            g.temp_color=c

        return render(request, self.template_name, {"groups": groups})


class GroupView(View):

    template_name = "groups/group.html"

    def get(self, request, *args, **kwargs):

        from django.db.models import Q

        group_id = kwargs.get("group_id", None)
        logger.info("GroupView %s" %group_id)
        group = get_object_or_404(Group, pk=group_id)
        #tracks = Track.objects.filter((Q(group__id=group_id) | Q(group_activity__id=group_id)) )
        tracks = Track.objects.filter(group__id=group_id)
        waypoints = Waypoint.objects.filter(track__group__id=group_id)
        # colors = get_colors(len(tracks))
        # for t,c in zip(tracks,colors):
        #     t.color_temp=c
  

        with_waypoints = request.GET.get('with_waypoints', False)
        with_photos = request.GET.get('with_photos', False)
        request_str = request.GET.urlencode()

        from .forms import GroupFormQuick
        form = GroupFormQuick(instance=group)

        infos_on_filtered_tracks = group.get_infos_on_filtered_tracks()

        return render(
            request,
            self.template_name,
            {
                "group": group,
                "tracks": tracks,
                "waypoints": waypoints,
                #"colors": colors,
                "form":form,
                "with_waypoints":with_waypoints,
                "with_photos":with_photos,
                "request":request_str,
                "infos_on_filtered_tracks":infos_on_filtered_tracks
            },
        )

    def post(self, request, *args, **kwargs):
        from .forms import GroupFormQuick
        from datetime import datetime

        group_id = kwargs.get("group_id", None)
        logger.info("GroupView post %s" % group_id)
        instance = get_object_or_404(Group, pk=group_id)
        form = GroupFormQuick(request.POST or None, instance=instance)

        if form.is_valid():
            f = form.save()
            group_id = f.pk
            group = get_object_or_404(Group, pk=group_id)
            group.set_attributes()

            return HttpResponseRedirect(
                reverse("group_detail", kwargs={"group_id": group_id})
            )
        else:
            return render(
                request, self.template_name, {"form": form, "has_error": True}
            )


class DeleteGroups(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages

        # if on delete=set_null is not working, I do this by hand
        # print("Deleting foreign keys")
        # for t in Track.objects.all():
        #     t.group=None
        #     t.group_activity=None
        #     t.save()

        logger.info("Deleting tracks")
        try:
            Group.objects.all().delete()
            logger.info("OK Deleting groups")
        except Exception as e:
            logger.error("KO deleting groups %s" %e)

        message = "All groups deleted"
        messages.success(request, message)

        return redirect(reverse("import"))

class CreateGroups(View):
    def get(self, request, *args, **kwargs):
        from .utils import cluster
        import threading
        from django.contrib import messages
        from .models import Group

        t = threading.Thread(target=cluster, args=(30,))
        t.start()

        message = "Groups are being created"
        messages.success(request, message)
        logger.info(message)

        return redirect(reverse("import"))

class CreateGroupView(View):

    template_name = "groups/group_edit.html"

    def get(self, request, *args, **kwargs):
        from .forms import GroupForm, GroupFormQuick

        form_id = kwargs.get("form", "normal")
        #print(form_id)
        if form_id=="quick":
            modelform=GroupFormQuick
        else:
            modelform = GroupForm
        group_id = kwargs.get("group_id", None)
        logger.info("CreateGroupView %s" %group_id)

        if group_id:
            group_ = Group.objects.get(pk=group_id)
            form = modelform(instance=group_)
            return render(
                request,
                self.template_name,
                {"group": group_, "group_id": group_id, "form": form},
            )
        else:
            track_ids_string = request.GET.get("track_ids", "")
            rule_ids_string = request.GET.get("rule_ids", "")

            if track_ids_string:
                string_list = track_ids_string.split("_")
            else:
                string_list=[]
            if rule_ids_string:
                rule_list = rule_ids_string.split("_")
            else:
                rule_list = []

            logger.info("CreateGroupView %s %s" %(string_list,rule_list ))
            track_ids = [int(s) for s in string_list]
            rule_ids = [int(s) for s in rule_list]

            from datetime import datetime
            now=datetime.now().strftime("%Y%m%d%H%MS")

            tracks=Track.objects.filter(pk__in=track_ids)
            rules=GroupRule.objects.filter(pk__in=rule_ids)
            
            form = modelform(
                initial={
                    "name": "Group "+ now,
                    "tracks":tracks,
                    "rules":rules
                }
            )

            return render(
                request, self.template_name, {"form": form, "group_id": group_id}
            )

    def post(self, request, *args, **kwargs):
        from .forms import GroupForm, GroupFormQuick
        from datetime import datetime

        form_id = kwargs.get("form", "normal")
        if form_id=="quick":
            modelform=GroupFormQuick
        else:
            modelform = GroupForm
        group_id = kwargs.get("group_id", None)
        logger.info("CreateGroupView post %s" %group_id)
        if group_id:
            instance = get_object_or_404(Group, pk=group_id)
            form = modelform(request.POST or None, instance=instance)
            new = False
        else:
            form = modelform(request.POST)
            new = True

        if form.is_valid():
            f = form.save()
            group_id = f.pk
            group = get_object_or_404(Group, pk=group_id)
            if new:
                group.add_tracks_from_rules()
            group.set_attributes()

            return HttpResponseRedirect(
                reverse("group_detail", kwargs={"group_id": group_id})
            )
        else:
            return render(
                request, self.template_name, {"form": form, "has_error": True}
            )


class DeleteGroupView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages

        group_id = kwargs.get("group_id", None)
        logger.info("DeleteGroupView %s" %group_id)
        group = get_object_or_404(Group, pk=group_id)
        group_name = group.name

        group.delete()

        message = "Group " + group_name + " deleted"
        logger.info(message)
        messages.success(request, message)

        return redirect(reverse("group_index"))


class ResaveGroupView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from .models import Group

        group_id = kwargs.get("group_id", None)
        group = get_object_or_404(Group, pk=group_id)
        logger.info("ResaveGroupView %s" % group.pk)

        group.set_attributes(refresh_all=True)

        return redirect(reverse("group_detail", args=(group_id,)))


class ResaveAllGroupsView(View):
    def get(self, request, *args, **kwargs):
        from django.contrib import messages
        from .models import Group

        logger.info("ResaveAllGroupsView")

        for group in Group.objects.all():
            logger.info(group.name)
            group.set_attributes()

        return redirect(reverse("group_index"))


class GroupPlotsView(View):

    template_name = "groups/group_plots.html"

    def get(self, request, *args, **kwargs):

        logger.info("GroupPlotsView")
        group_id = kwargs.get("group_id", None)
        group = get_object_or_404(Group, pk=group_id)
        from tracks.utils import get_options
        options=get_options()

        return render(
            request,
            self.template_name,
            {
                "group": group,
                "options":options
            },
        )

class GroupStatisticsView(View):

    template_name = "groups/group_statistics.html"

    def get(self, request, *args, **kwargs):

        logger.info("GroupStatisticsView")
        group_id = kwargs.get("group_id", None)
        group = get_object_or_404(Group, pk=group_id)

        return render(
            request,
            self.template_name,
            {
                "group": group,
            },
        )

class GroupFromSearchView(View):

    template_name = "groups/group_from_search.html"

    def get(self, request, *args, **kwargs):

        logger.debug("GroupFromSearchView")
        Model=GroupRule

        try:
            import urllib
            initial_string = "?" + urllib.parse.urlencode(request.GET)
        except:
            initial_string = "?"

        return render(
            request, self.template_name, {"initial_string": initial_string}
        )

    def post(self, request, *args, **kwargs):
        from .models import GroupRule as Model

        name=request.POST.get("name","")
        query_string=request.POST.get("query_string","")

        if name and query_string:
            rule = GroupRule(
                name=name,
                query_string=query_string,
            )
            rule.save()
            group = Group(
                name=name,
                auto_update_properties=True,
            )
            group.save()
            group.rules.add(rule)
            group.add_tracks_from_rules()
            group.set_attributes()
            
            return HttpResponseRedirect(
                reverse("group_detail", kwargs={"group_id": group.pk})
            )


## autocomplete
from dal import autocomplete

class GroupAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !

        qs = Group.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q).order_by("-pk")

        return qs

class GroupRuleAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !

        qs = GroupRule.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q).order_by("-pk")

        return qs


## group  + rules
class GroupAddTracksFromRulesView(View):
    def get(self, request, *args, **kwargs):
        logger.info("GroupAddTracksFromRulesView")
        group_id = kwargs.get("group_id", None)
        group = get_object_or_404(Group, pk=group_id)

        track_names=group.add_tracks_from_rules()

        messages.success(request, "%s tracks added: %s" %(len(track_names),track_names))

        return redirect(reverse("group_detail", args=(group_id,)))

## rules
class GroupRulesView(View):

    template_name = "groups/group_rules.html"

    def get(self, request, *args, **kwargs):
        logger.debug("GroupRulesView")
        rules = GroupRule.objects.all()

        return render(request, self.template_name, {"rules": rules})

class GroupRuleView(View):

    template_name = "groups/group_rule.html"

    def get(self, request, *args, **kwargs):
        id = kwargs.get("rule_id", None)

        print(request.GET)

        logger.debug("GroupRuleView")
        Model=GroupRule

        if id:
            from .forms import GroupRuleForm as ModelForm
            object = Model.objects.get(pk=id)
            form = ModelForm(instance=object )

            n_tracks = object.filtered_tracks().count()

            return render(
                request,
                self.template_name,
                {"obj": object, "id": id, "form": form,"n_tracks":n_tracks},
            )
        else:
            try:
                import urllib
                initial_string = "?" + urllib.parse.urlencode(request.GET)
            except:
                initial_string = "?"

            all_rules=GroupRule.objects.all()
            
            from .forms import GroupRuleForm as ModelForm
            form = ModelForm(initial={'query_string': initial_string})
            return render(
                request, self.template_name, {"form": form, "id": id,"all_rules":all_rules}
            )

    def post(self, request, *args, **kwargs):
        from .models import GroupRule as Model

        id = kwargs.get("rule_id", None)

        if id:
            from .forms import GroupRuleForm as ModelForm
            instance = get_object_or_404(Model, pk=id)
            form = ModelForm(request.POST or None, instance=instance)
            new = False
            logger.info("Modify object %s" % id)
        else:
            # in the form for a new object, I can select an old object to edit
            from .forms import GroupRuleForm as ModelForm
            id_to_edit = request.POST.get("rule_choice", None)
            if id_to_edit:
                instance=get_object_or_404(Model, pk=id_to_edit)
                form = ModelForm(request.POST or None, instance=instance)
                logger.info("Editing object %s" %instance)
            else:
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
                reverse("group_rules")
            )
        else:
            logger.error("Form")
            return render(
                request, self.template_name, {"form": form, "has_error": True}
            )

class GroupRuleDeleteView(View):

    def get(self, request, *args, **kwargs):

        id = kwargs.get("rule_id", None)

        logger.debug("GroupRuleDeleteView")


        rule = GroupRule.objects.get(pk=id)
        rule_name = rule.name
        rule.delete()

        message = "Rule %s deleted" %rule_name
        messages.success(request, message)

        return HttpResponseRedirect(
            reverse("group_rules")
        )

from django import forms
from .models import *
from tracks.models import Track
from django.contrib.admin.widgets import FilteredSelectMultiple
import os
from django.conf import settings
from dal import autocomplete


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group

        fields = ["name","tracks","exclude_from_search", "auto_update_properties","use_points_instead_of_lines","hide_in_forms","always_use_lines","rules","rules_act_as_and"]
        widgets = {"tracks":autocomplete.ModelSelect2Multiple(url='track-autocomplete') ,
                    'rules': autocomplete.ModelSelect2Multiple(url='group_rule-autocomplete') }

    # class Media:
    #     css = {
    #         'all': (os.path.join(settings.BASE_DIR, '/static/admin/css/widgets.css'),),
    #     }
    #     js = ('/admin/jsi18n'),
    #
    # def __init__(self, *args, **kwargs):
    #     super(GroupForm, self).__init__(*args, **kwargs)
    #
    #     self.fields['tracks'] = forms.ModelMultipleChoiceField(
    #         queryset=Track.objects.all(),
    #         widget=
    #         required=False)


class GroupFormQuick(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name","exclude_from_search","auto_update_properties","use_points_instead_of_lines","hide_in_forms","always_use_lines","rules","rules_act_as_and"]
        widgets = {'rules':  autocomplete.ModelSelect2Multiple(url='group_rule-autocomplete') }

class GroupRuleForm(forms.ModelForm):
    class Meta:
        model = GroupRule
        fields = ["name","query_string"]

from django import forms
from .models import *

class QuickImportForm(forms.ModelForm):
    class Meta:
        model = QuickImport
        fields = ["name","steps", "active"]
    steps = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=True, queryset=ImportStep.objects.all())        

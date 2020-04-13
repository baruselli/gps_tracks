from django import forms
from .models import Line

class LineForm(forms.ModelForm):
    class Meta:
        model = Line
        fields = ["lats_text", "long_text","alts_text", "name","closed","line_type","is_global"]
from django import forms

from .models import Report


class UpdateReportForm(forms.ModelForm):
    class Meta:
        model = Report
        exclude = ('is_filled', 'work_shift')

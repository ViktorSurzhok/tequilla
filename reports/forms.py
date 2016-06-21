from django import forms

from .models import Report


class UpdateReportForm(forms.ModelForm):
    class Meta:
        model = Report
        exclude = ('filled_date', 'work_shift')
        localized_fields = ('__all__')


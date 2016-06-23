from django import forms

from .models import Report, ReportTransfer


class UpdateReportForm(forms.ModelForm):
    class Meta:
        model = Report
        exclude = ('filled_date', 'work_shift')
        localized_fields = ('__all__')


class ReportTransferForm(forms.ModelForm):
    class Meta:
        model = ReportTransfer
        fields = ('total_sum', 'transfer_type', 'comment', 'start_week', 'employee')
        widgets = {'start_week': forms.HiddenInput(), 'employee': forms.HiddenInput()}
        localized_fields = ('__all__')


class ReportTransferFormForAdmin(forms.ModelForm):
    class Meta:
        model = ReportTransfer
        fields = ('total_sum', 'transfer_type', 'comment', 'is_accepted', 'start_week', 'employee')
        widgets = {
            'start_week': forms.HiddenInput(),
            'employee': forms.HiddenInput(),
            'is_accepted': forms.CheckboxInput()
        }
        localized_fields = ('__all__')
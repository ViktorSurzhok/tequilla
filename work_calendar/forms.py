from django import forms

from work_calendar.models import WorkShift


class WorkShiftForm(forms.ModelForm):
    """
    Форма добавления\редактирования рабочй смены
    """

    class Meta:
        model = WorkShift
        fields = ('club', 'date', 'special_config', 'employee', 'start_time', 'end_time', 'comment', 'probation')

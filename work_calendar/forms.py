from django import forms
from django.contrib.auth.models import Group

from work_calendar.models import WorkShift


class WorkShiftForm(forms.ModelForm):
    """
    Форма добавления\редактирования рабочй смены
    """

    employee = forms.ModelChoiceField(
        queryset=Group.objects.get(name='employee').user_set.filter(is_active=True), required=True, label='Сотрудник'
    )

    class Meta:
        model = WorkShift
        fields = ('club', 'date', 'special_config', 'employee', 'start_time', 'end_time', 'comment', 'probation')

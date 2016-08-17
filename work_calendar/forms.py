from django import forms
from django.db.models import Q

from extuser.models import ExtUser
from work_calendar.models import WorkShift


class WorkShiftForm(forms.ModelForm):
    """
    Форма добавления\редактирования рабочй смены
    """

    employee = forms.ModelChoiceField(
        queryset=ExtUser.objects.filter(
            Q(groups__name='coordinator') | Q(groups__name='employee')
        ).filter(is_active=True).all(),
        required=True,
        label='Сотрудник'
    )

    class Meta:
        model = WorkShift
        fields = ('club', 'date', 'special_config', 'employee', 'start_time', 'end_time', 'comment', 'probation')

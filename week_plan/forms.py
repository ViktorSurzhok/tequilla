from django import forms

from club.models import Club
from extuser.models import ExtUser
from week_plan.models import PlanForDay
from work_calendar.models import WorkShift


class PlanForDayForm(forms.ModelForm):
    employee = forms.ChoiceField(
        required=False,
        choices=[(u.id, u.get_full_name()) for u in ExtUser.objects.filter(is_active=True)],
        label='Tequilla girl'
    )

    def __init__(self, *args, **kwargs):
        super(PlanForDayForm, self).__init__(*args, **kwargs)
        # в выборку загрузить рабочие смены только для выбранного дня
        if 'initial' in kwargs:
            self.fields['work_shift'].queryset = WorkShift.objects.filter(date=kwargs['initial']['date'])
        self.fields['club'].queryset = Club.objects.filter(is_active=True)

    class Meta:
        model = PlanForDay
        fields = ('club', 'employee', 'date', 'work_shift', 'start_time', 'end_time', 'comment')

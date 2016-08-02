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
        self.fields['club'].queryset = Club.objects.filter(is_active=True)

    class Meta:
        model = PlanForDay
        fields = ('club', 'employee', 'date', 'start_time', 'end_time', 'comment')

from django import forms
from django.contrib.auth.models import Group

from penalty.models import PenaltyType, MainPenaltySchedule, Penalty


class PenaltyTypeForm(forms.ModelForm):
    class Meta:
        model = PenaltyType
        fields = ('description', 'sum',  'dismissal', 'num')


class MainPenaltyScheduleForm(forms.ModelForm):
    class Meta:
        model = MainPenaltySchedule
        fields = ('type', 'day_of_week')
        widgets = {
            'type': forms.HiddenInput(
                attrs={'required': False, 'readonly': True}
            ),
            'day_of_week': forms.Select(
                attrs={'required': True, 'class': 'form-control'}
            ),
        }


class PenaltyForm(forms.ModelForm):

    employee = forms.ModelChoiceField(
        queryset=Group.objects.get(name='employee').user_set.filter(is_active=True), required=True, label='Tequilla girl'
    )

    class Meta:
        model = Penalty
        fields = ('employee', 'type', 'date', 'count', 'was_paid')

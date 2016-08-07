from django import forms

from calculator.models import CalculatorState, DrinkForState
from reports.models import Report


class CalculatorStateForm(forms.ModelForm):
    class Meta:
        model = CalculatorState
        fields = ('club', 'date', 'start_time', 'end_time', 'discount')


class DrinkForStateForm(forms.ModelForm):
    state = forms.ChoiceField(choices=CalculatorState.objects.all())

    class Meta:
        model = DrinkForState
        fields = ('state', 'drink', 'price_in_bar', 'volume')


class ImportToReport(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('start_time', 'end_time', 'sum_for_bar', 'discount')

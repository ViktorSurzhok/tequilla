from django import forms

from calculator.models import CalculatorState, DrinkForState


class CalculatorStateForm(forms.ModelForm):
    class Meta:
        model = CalculatorState
        fields = ('club', 'date', 'start_time', 'end_time')


class DrinkForStateForm(forms.ModelForm):
    state = forms.ChoiceField(choices=CalculatorState.objects.all())

    class Meta:
        model = DrinkForState
        fields = ('state', 'drink', 'price_in_bar', 'volume')

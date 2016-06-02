from django import forms

from schedule.models import WorkDay


class WorkDayForm(forms.ModelForm):
    """
    Форма добавления\редактирования рабочего дня в график.
    """
    class Meta:
        model = WorkDay
        fields = ('employee', 'date', 'time', 'cant_work', 'comment')

        widgets = {
            'date': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'disabled': True}),
            'employee': forms.HiddenInput(attrs={'class': 'form-control', 'required': True}),
            'time': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'cant_work': forms.CheckboxInput(attrs={'class': 'flat'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

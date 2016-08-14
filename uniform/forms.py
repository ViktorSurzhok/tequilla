from django import forms
from django.contrib.auth.models import Group

from uniform.models import Uniform, UniformForEmployee


class UniformEditForm(forms.ModelForm):
    class Meta:
        model = Uniform
        fields = ('name', 'num', 'price')


class CreateUniformForEmployee(forms.ModelForm):
    employee = forms.ModelChoiceField(
        queryset=Group.objects.get(name='employee').user_set.filter(is_active=True), required=True, label='Tequilla girl'
    )

    class Meta:
        model = UniformForEmployee
        fields = ('employee', 'uniform', 'count', 'date', 'is_probation', 'group')

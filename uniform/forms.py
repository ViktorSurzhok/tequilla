from django import forms

from uniform.models import Uniform


class UniformEditForm(forms.ModelForm):
    class Meta:
        model = Uniform
        fields = ('name', 'num')

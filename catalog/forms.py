from django import forms

from catalog.models import FakeCity


class FakeCityForm(forms.ModelForm):
    class Meta:
        model = FakeCity
        fields = ('name',)

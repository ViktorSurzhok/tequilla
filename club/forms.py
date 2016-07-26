from django import forms
from django.forms.models import inlineformset_factory

from club.models import Club, ClubType, DayOfWeek, Drink, Metro
from extuser.models import ExtUser


class ClubImportForm(forms.ModelForm):
    """
    Форма добавления клуба.
    Используется при импорте данных из старой системы
    """
    class Meta:
        model = Club
        exclude = ('photo',)


class ClubEditAdminForm(forms.ModelForm):
    """
    Форма для редактирования данных клубов.
    Используется РУКОВОДСТВОМ.
    """
    employee = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=ExtUser.objects.filter(is_active=True),
        label='Сотрудники',
        required=False
    )
    type = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=ClubType.objects.all(),
        label='Тип заведения',
        required=False
    )
    days_of_week = forms.ModelMultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(),
        queryset=DayOfWeek.objects.all(),
        label='Дни недели',
        required=False
    )

    class Meta:
        model = Club
        exclude = ('old_id',)


class ClubTypeForm(forms.ModelForm):
    class Meta:
        model = ClubType
        fields = ('name',)


class MetroForm(forms.ModelForm):
    class Meta:
        model = Metro
        fields = ('name',)


DrinkFormSet = inlineformset_factory(Club, Drink, fields='__all__', extra=0, widgets={
    'name': forms.TextInput(attrs={'class': 'form-control'}),
    'price_in_bar': forms.TextInput(attrs={'class': 'form-control'}),
    'price_for_sale': forms.TextInput(attrs={'class': 'form-control'}),
})

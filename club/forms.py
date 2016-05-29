from django import forms

from club.models import Club


class ClubImportForm(forms.ModelForm):
    """
    Форма добавления клуба.
    Используется при импорте данных из старой системы
    """
    class Meta:
        model = Club
        exclude = ('photo',)

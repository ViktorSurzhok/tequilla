from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import get_user_model

from extuser.models import ExtUser


class UserImportForm(forms.ModelForm):
    """
    Форма добавления пользователя
    """

    def save(self, commit=True):
        user = super(UserImportForm, self).save(commit=False)
        user.set_password('secret' + str(self.cleaned_data['old_id']))
        if commit:
            user.save()

        return user

    class Meta:
        model = ExtUser
        exclude = ('avatar', 'password')


class UserCreationForm(forms.ModelForm):
    """
    Форма добавления пользователя которая используется на странице регистрации
    """
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'})
    )
    confirm_password = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Подтверждение пароля'})
    )

    class Meta:

        model = ExtUser

        # Note - include all *required* MyUser fields here,
        # but don't need to include password and confirm_password as they are
        # already included since they are defined above.
        fields = ('surname', 'name', 'email', 'phone', 'vkontakte')

        widgets = {
            'surname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия', 'required': True}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-mail'}),
            'phone': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Мобильный телефон (Без +7 и 8)', 'required': True}
            ),
            'vkontakte': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'id Вконтакте'}),
        }

    def clean(self):
        if 'confirm_password' in self.cleaned_data:
            if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
                self.add_error('confirm_password', 'Введённые пароли не совпадают')

        return super().clean()

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()

        return user


class UserChangeForm(forms.ModelForm):
    """
    Форма для обновления данных пользователей. Нужна только для того, чтобы не
    видеть постоянных ошибок "Не заполнено поле password" при обновлении данных
    пользователя.
    """

    def save(self, commit=True):
        user = super(UserChangeForm, self).save(commit=False)
        if commit:
            user.save()
        return user

    class Meta:
        model = get_user_model()
        fields = ('surname', 'name', 'gender', 'email', 'phone', 'vkontakte')

        classes = 'form-control col-md-7 col-xs-12'
        widgets = {
            'surname': forms.TextInput(
                attrs={'class': classes, 'required': True, 'data-parsley-id': '1'}
            ),
            'name': forms.TextInput(
                attrs={'class': classes, 'required': True, 'data-parsley-id': '2'}
            ),
            'gender': forms.Select(
                attrs={'class': classes, 'required': True, 'data-parsley-id': '3'}
            ),
            'email': forms.EmailInput(
                attrs={'class': classes, 'data-parsley-id': '4'}
            ),
            'phone': forms.TextInput(
                attrs={'class': classes, 'required': True, 'data-parsley-id': '5'}
            ),
            'vkontakte': forms.TextInput(
                attrs={'class': classes, 'data-parsley-id': '6'}
            ),
        }


class LoginForm(forms.Form):
    """
    Форма для входа в систему
    """
    phone = forms.CharField(
        label='Номер телефона',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Номер телефона'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'})
    )


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        label='Текущий пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Текущий пароль', 'required': True})
    )
    new_password = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Новый пароль', 'required': True})
    )
    confirm_password = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите пароль', 'required': True})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_current_password(self):
        valid = self.user.check_password(self.cleaned_data['current_password'])
        if not valid:
            self.add_error('current_password', "Неверный текущий пароль.")
        return valid

    def clean(self):
        if 'new_password' in self.cleaned_data:
            if 'confirm_password' in self.cleaned_data:
                if self.cleaned_data['new_password'] != self.cleaned_data['confirm_password']:
                    self.add_error('confirm_password', 'Введённые пароли не совпадают')
            else:
                self.add_error('confirm_password', 'Обязательное поле')
        else:
            self.add_error('new_password', 'Обязательное поле')
        return super().clean()

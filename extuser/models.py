from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group, Permission
from django.contrib.auth.models import PermissionsMixin
from django.contrib.contenttypes.models import ContentType
from django.db import models
from model_utils.models import TimeStampedModel


class ExtUser(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    GENDER_CHOICES = (
        ('female', 'Женский'),
        ('male', 'Мужской')
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=255,
        blank=True
    )
    avatar = models.ImageField(
        'Аватар',
        blank=True,
        null=True,
        upload_to="avatar"
    )
    name = models.CharField(
        'Имя',
        max_length=40
    )
    surname = models.CharField(
        'Фамилия',
        max_length=40
    )
    phone = models.CharField(
        'Номер телефона',
        max_length=30,
        unique=True,
        db_index=True
    )
    additional_phone = models.CharField(
        'Доп. телефон',
        max_length=30,
        blank=True
    )
    vkontakte = models.CharField(
        'ID вконтакте',
        max_length=200,
        blank=True
    )
    is_active = models.BooleanField(
        'Активен',
        default=False
    )
    # true - мужской пол, false - женский
    gender = models.CharField('Пол', max_length=10, default='female', choices=GENDER_CHOICES)

    # Этот метод обязательно должен быть определён
    def get_full_name(self):
        return self.surname + ' ' + self.name

    def get_short_name(self):
        return self.surname

    def __str__(self):
        return self.surname + ' ' + self.name

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['surname', 'name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

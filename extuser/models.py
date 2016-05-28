import os
import random
import urllib

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group, Permission, \
    UserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.db import models
from model_utils.models import TimeStampedModel

from tequilla import settings


class ExtUser(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    GENDER_CHOICES = (
        ('female', 'Женский'),
        ('male', 'Мужской')
    )
    email = models.EmailField('Электронная почта', max_length=255, blank=True)
    avatar = models.ImageField('Аватар', blank=True, null=True, upload_to="avatar")
    #avatar width
    #avatar crop data
    #avatar_cropped
    name = models.CharField('Имя', max_length=40)
    surname = models.CharField('Фамилия', max_length=40)
    phone = models.CharField('Номер телефона', max_length=30, unique=True, db_index=True)
    additional_phone = models.CharField('Доп. телефон', max_length=30, blank=True)
    vkontakte = models.CharField('ID вконтакте', max_length=200, blank=True)
    is_active = models.BooleanField('Активен', default=False)
    pledge = models.CharField('Залог', blank=True, null=True, max_length=100)
    coordinator = models.ForeignKey('self', blank=True, null=True)
    pay_to_coord = models.BooleanField('Платить координатору', default=False)
    old_id = models.PositiveIntegerField('ID из старой системы', blank=True, null=True)
    gender = models.CharField('Пол', max_length=10, default='female', choices=GENDER_CHOICES)

    objects = UserManager()

    # Этот метод обязательно должен быть определён
    def get_full_name(self):
        return self.surname + ' ' + self.name

    def get_short_name(self):
        return self.surname

    def __str__(self):
        return self.surname + ' ' + self.name

    def get_default_avatar(self):
        return settings.DEFAULT_AVATAR

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['surname', 'name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Album(TimeStampedModel):
    """
    Албом с фотографиями Photo
    """
    name = models.CharField(max_length=255, verbose_name='Название')
    user = models.ForeignKey(ExtUser, related_name='albums')
    old_id = models.PositiveIntegerField(
        'ID из старой системы',
        blank=True,
        null=True
    )


class Photo(TimeStampedModel):
    """
    Класс фотографий.
    Каждая фотография привязана к альбому.
    """
    def get_upload_path(self, filename):
        usr = str(self.user.id)
        return os.path.join('albums', '%s' % usr, str(random.randint(1, 100000)) + '_' + filename)

    file = models.ImageField(upload_to=get_upload_path, verbose_name='Изображение')
    album = models.ForeignKey(Album, related_name='photos', blank=True, null=True)
    user = models.ForeignKey(ExtUser, related_name='photos')
    url = models.CharField(max_length=255, blank=True, null=True)
    old_id = models.PositiveIntegerField(
        'ID из старой системы',
        blank=True,
        null=True
    )
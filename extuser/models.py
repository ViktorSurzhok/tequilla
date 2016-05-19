from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group, Permission
from django.contrib.auth.models import PermissionsMixin
from django.contrib.contenttypes.models import ContentType
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, phone, password=None):
        if not self.phone:
            raise ValueError('Номер телефона должен быть указан')

        user = self.model(phone=phone)
        user.set_password(password)
        group = Group.objects.get(name='employee')
        user.groups.add(group)
        user.save(using=self._db)
        return user


class ExtUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        'Электронная почта',
        max_length=255,
        unique=True,
        blank=True
    )
    avatar = models.ImageField(
        'Аватар',
        blank=True,
        null=True,
        upload_to="user/avatar"
    )
    firstname = models.CharField(
        'Фамилия',
        max_length=40,
        null=True,
        blank=True
    )
    lastname = models.CharField(
        'Имя',
        max_length=40
    )
    phone = models.CharField(
        'Номер телефона',
        max_length=30,
        unique=True,
        db_index=True
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

    # Этот метод обязательно должен быть определён
    def get_full_name(self):
        return self.firstname + ' ' + self.lastname

    def get_short_name(self):
        return self.lastname

    def __str__(self):
        return self.firstname + ' ' + self.lastname

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

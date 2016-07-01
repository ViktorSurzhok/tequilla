from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group, Permission, \
    UserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.contenttypes.models import ContentType
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
    avatar_cropped = models.ImageField('Обрезанный аватар', blank=True, null=True, upload_to="cr_avatar")
    name = models.CharField('Имя', max_length=40)
    surname = models.CharField('Фамилия', max_length=40)
    phone = models.CharField('Номер телефона', max_length=30, unique=True, db_index=True)
    additional_phone = models.CharField('Доп. телефон', max_length=30, blank=True)
    vkontakte = models.CharField('ID вконтакте', max_length=200, blank=True)
    is_active = models.BooleanField('Активен', default=False)
    pledge = models.CharField('Залог', blank=True, null=True, max_length=100)
    coordinator = models.ForeignKey('self', blank=True, null=True, verbose_name='Координатор')
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

    def get_small_avatar(self):
        return self.avatar_cropped.url if self.avatar_cropped else settings.DEFAULT_AVATAR_SMALL

    def get_vkontakte_link(self):
        return self.vkontakte if self.vkontakte.startswith('http://') else 'http://vk.com/' + self.vkontakte

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['surname', 'name']

    class Meta:
        ordering = ('surname',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class UserActivityLog(TimeStampedModel):
    """
    Хранит время входа пользователя в систему.
    Статистику по времени входа каждого пользователя может просматривать руководство в профиле сотрудника.
    """
    user = models.ForeignKey(ExtUser, related_name='activity_logs')


class PenaltyType(TimeStampedModel):
    """
    Тип штрафа.
    """
    description = models.TextField('Описание')
    sum = models.IntegerField('Сумма')
    num = models.PositiveSmallIntegerField('Номер', default=0)
    dismissal = models.BooleanField('Возможно увольнение', default=False)

    def __str__(self):
        return self.description

    class Meta:
        ordering = ('num',)


class MainPenaltySchedule(TimeStampedModel):
    """
    График проставления штрафов по умолчанию
    """
    SCHEDULE_TYPE_CHOICE = 'schedule'
    REPORT_TYPE_CHOICE = 'report'
    TYPE_CHOICES = (
        (SCHEDULE_TYPE_CHOICE, 'График'),
        (REPORT_TYPE_CHOICE, 'Отчеты')
    )

    type = models.CharField('Тип', max_length=10, choices=TYPE_CHOICES)
    day_of_week = models.ForeignKey('club.DayOfWeek', verbose_name='День недели', blank=True, null=True)
    start_week = models.DateField('Дата начала недели за которую написан перевод', blank=True, null=True)

    def type_verbose(self):
        return dict(MainPenaltySchedule.TYPE_CHOICES)[self.type]

    @staticmethod
    def get_settings():
        obj, created = MainPenaltySchedule.objects.get_or_create(
            type=MainPenaltySchedule.SCHEDULE_TYPE_CHOICE, start_week=None
        )
        obj2, created = MainPenaltySchedule.objects.get_or_create(
            type=MainPenaltySchedule.REPORT_TYPE_CHOICE, start_week=None
        )
        return [obj, obj2]

    @staticmethod
    def get_settings_by_week(start_week):
        obj, created = MainPenaltySchedule.objects.get_or_create(
            type=MainPenaltySchedule.SCHEDULE_TYPE_CHOICE, start_week=start_week
        )
        obj2, created = MainPenaltySchedule.objects.get_or_create(
            type=MainPenaltySchedule.REPORT_TYPE_CHOICE, start_week=start_week
        )
        return [obj, obj2]

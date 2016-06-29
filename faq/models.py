from django.db import models
from model_utils.models import TimeStampedModel

from extuser.models import ExtUser


class Post(TimeStampedModel):
    name = models.CharField('Название', max_length=255)
    description = models.TextField('Краткое описание')
    content = models.TextField('Содержимое')
    old_id = models.PositiveIntegerField('ID из старой системы', blank=True, null=True)

    def __str__(self):
        return self.name


class Comment(TimeStampedModel):
    post = models.ForeignKey(Post, related_name='comments')
    employee = models.ForeignKey(ExtUser)
    content = models.TextField('Комментарий')
    parent = models.ForeignKey('self', related_name='childrens', blank=True, null=True)
    old_id = models.PositiveIntegerField('ID из старой системы', blank=True, null=True)

    def __str__(self):
        return self.content[:50]


class Menu(TimeStampedModel):
    name = models.CharField('Название', max_length=255)
    parent = models.ForeignKey(
        'self', related_name='childrens', blank=True, null=True, verbose_name='Родительское меню'
    )
    post = models.ForeignKey(
        Post, verbose_name='Привязка к записи', blank=True, null=True
    )
    order = models.SmallIntegerField

    def __str__(self):
        return self.name

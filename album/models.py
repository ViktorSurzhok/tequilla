import os
import random

from model_utils.models import TimeStampedModel
from django.db import models
from extuser.models import ExtUser


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

    class Meta:
        ordering = ('-created',)


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

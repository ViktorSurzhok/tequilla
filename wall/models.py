import os
import random

from django.db import models
from model_utils.models import TimeStampedModel
from sorl.thumbnail import ImageField

from extuser.models import ExtUser


class Post(TimeStampedModel):
    text = models.TextField(verbose_name='Текст сообщения', blank=True)
    parent = models.ForeignKey('self', related_name='childrens', blank=True, null=True)
    user = models.ForeignKey(ExtUser)
    old_id = models.PositiveIntegerField('ID из старой системы', blank=True, null=True)

    class Meta:
        ordering = ('-created',)


class Photo(TimeStampedModel):
    def get_upload_path(self, filename):
        slug = str(self.post.id)
        return os.path.join('posts_img', '%s' % slug, str(random.randint(1, 1000000)) + '_' + filename)

    file = ImageField(upload_to=get_upload_path, verbose_name='Изображение')
    post = models.ForeignKey(Post, related_name='images')

from django.db import models
from model_utils.models import TimeStampedModel

from extuser.models import ExtUser


class Message(TimeStampedModel):
    from_user = models.ForeignKey(ExtUser, verbose_name='Отправитель', related_name='my_messages')
    to_user = models.ForeignKey(ExtUser, verbose_name='Получатель', related_name='messages_for_me')
    text = models.TextField('Текст сообщения', blank=True)
    was_read = models.BooleanField('Было прочитано', default=False)


class FilesForMessage(TimeStampedModel):
    """ Файлы привязываемые к личному сообщению
    """
    file = models.FileField(verbose_name='Файл', upload_to='')
    message = models.ForeignKey(Message)

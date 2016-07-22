import os
import random

from django.db import models
from model_utils.models import TimeStampedModel

from extuser.models import ExtUser


class Message(TimeStampedModel):
    from_user = models.ForeignKey(ExtUser, verbose_name='Отправитель', related_name='my_messages')
    to_user = models.ForeignKey(ExtUser, verbose_name='Получатель', related_name='messages_for_me')
    text = models.TextField('Текст сообщения', blank=True)
    was_read = models.BooleanField('Было прочитано', default=False)
    is_transfered = models.BooleanField(default=False)

    def get_short_text(self):
        return self.text[:77] + '...' if len(self.text) > 80 else self.text


class FilesForMessage(TimeStampedModel):
    """ Файлы привязываемые к личному сообщению
    """
    def get_upload_path(self, filename):
        usr = str(self.message.from_user.id)
        return os.path.join('message_files', '%s' % usr, str(random.randint(1, 100000)) + '_' + filename)

    file = models.FileField(verbose_name='Файл', upload_to=get_upload_path)
    message = models.ForeignKey(Message, related_name='files')

    def get_file_name(self):
        return self.file.name.split('/')[-1]

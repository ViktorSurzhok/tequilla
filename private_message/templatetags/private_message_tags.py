from django import template
from django.db.models import Max

from private_message.models import Message

register = template.Library()


@register.inclusion_tag('private_message/_new_messages_header.html')
def show_new_messages(user):
    query = 'SELECT * FROM private_message_message WHERE id IN (SELECT MAX(id) ' \
            'FROM private_message_message WHERE was_read=FALSE AND to_user_id = {} GROUP BY from_user_id) ' \
            'ORDER BY private_message_message.created DESC'.format(user.id)
    messages = Message.objects.raw(query)
    return {'messages': messages, 'messages_count': len(list(messages))}

from django import template
from ..models import ExtUser

register = template.Library()


@register.inclusion_tag('tags/sidebar.html')
def get_sidebar(user):
    return {'user_groups': user.groups.all().values_list('name', flat=True), 'user': user}

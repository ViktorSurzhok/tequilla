from django import template

from faq.models import Menu
from ..models import ExtUser

register = template.Library()


@register.inclusion_tag('tags/sidebar.html')
def get_sidebar(user):
    return {
        'user_groups': user.groups.all().values_list('name', flat=True),
        'user': user,
        'additional_menu': Menu.objects.filter(parent__isnull=True)
    }


@register.filter(name='display')
def display_value(bf):
    """Returns the display value of a BoundField"""
    return dict(bf.field.choices).get(bf.value(), '')

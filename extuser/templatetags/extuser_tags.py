from django import template

from faq.models import Menu
from penalty.models import Penalty
from ..models import ExtUser

register = template.Library()


@register.inclusion_tag('tags/sidebar.html')
def get_sidebar(user):
    return {
        'user_groups': user.groups.all().values_list('name', flat=True),
        'user': user,
        'have_unpaid_penalty': Penalty.objects.filter(employee=user, was_paid=False).exists(),
        'additional_menu': Menu.objects.filter(parent__isnull=True)
    }


@register.filter(name='display')
def display_value(bf):
    """Returns the display value of a BoundField"""
    return dict(bf.field.choices).get(bf.value(), '')

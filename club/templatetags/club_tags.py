from django import template

register = template.Library()


@register.filter
def add_http(value):
    return value if value.startswith('http') else 'http://' + value
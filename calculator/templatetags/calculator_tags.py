from django import template

register = template.Library()


# @register.simple_tag(takes_context=True)
# def check_selected(drink_id, selected_drink):
#     return value if value.startswith('http') else 'http://' + value
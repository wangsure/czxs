#from django import template
from django.template.defaultfilters import register
from django import template

register = template.Library()

@register.filter
def demo(value):
    return value + 'demo'

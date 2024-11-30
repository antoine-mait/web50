from django import template
import re 
register = template.Library()

@register.filter(name='get_item')
def get_item(value, arg):
    """ Retrieves an item from a dictionary """
    return value.get(arg, "")

@register.filter(name='replace')
def replace(value, arg):
    """ Replaces an underscore with a space """
    return value.replace(arg, " ")

@register.filter(name='remove_prefix')
def remove_prefix(value):
    """ Removes any numeric prefix followed by an underscore from a string """
    return re.sub(r'^\d+_', '', value)
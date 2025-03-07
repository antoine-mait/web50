from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Fetch the value from dictionary by key."""
    return dictionary.get(key)

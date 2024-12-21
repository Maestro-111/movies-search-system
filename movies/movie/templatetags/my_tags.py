from django import template

register = template.Library()


@register.filter
def get_dict_value(dictionary, key):
    """
    Custom filter to retrieve a value from a dictionary by key in templates.
    """
    if dictionary and key in dictionary:
        return dictionary.get(key)
    return None

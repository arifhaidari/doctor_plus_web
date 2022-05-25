from django import template

register = template.Library()


@register.filter
def get_index(obj, index):
    """
    Try to get value from a list object with an index given in parameter.
    Return an empty string if index doesn't exist
    """
    try:
        return obj[index]
    except IndexError:
        return ""

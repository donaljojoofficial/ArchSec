from django import template
import json

register = template.Library()

@register.filter(name='pretty_json')
def pretty_json(value):
    """
    Formats a dictionary as a pretty-printed JSON string.
    """
    if isinstance(value, dict):
        return json.dumps(value, indent=4)
    return value

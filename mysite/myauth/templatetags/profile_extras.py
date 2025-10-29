from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def profile_field(value, default_text="Не указано"):
    if value:
        return value
    else:
        return mark_safe(f"<em>{default_text}</em>")

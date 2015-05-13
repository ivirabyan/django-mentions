from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from ..utils import urlize_mentions as do_urlize_mentions, plain_mentions as do_plain_mentions


register = template.Library()


@register.filter(needs_autoescape=True)
def urlize_mentions(text, autoescape=None):
    if autoescape:
        text = conditional_escape(text)
    return mark_safe(do_urlize_mentions(text))


@register.filter(is_safe=True)
def plain_mentions(text):
    return do_plain_mentions(text)

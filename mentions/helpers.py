import jinja2
from jingo import register

from .utils import (urlize_mentions as do_urlize_mentions, get_mentions,
                    plain_mentions as do_plain_mentions)


@register.filter
def urlize_mentions(text, prefetched=None, urlize=None):
    rv = do_urlize_mentions(text, prefetched=prefetched, urlize=urlize)
    return jinja2.Markup(rv)


@register.filter
def plain_mentions(text):
    return do_plain_mentions(text)


@register.function
def prefetch_mentions(object_list, attr):
    texts = [getattr(obj, attr) for obj in object_list]
    return get_mentions(''.join(texts))

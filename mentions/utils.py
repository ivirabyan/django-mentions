import re
from .registry import providers

MENTION_PATTERN = re.compile('@\[(?P<title>[^\]]+)\]\((\w+):(\d+)\)')


def urlize_mentions(text, prefetched=None, urlize=None):
    if urlize is None:
        urlize = lambda url, title: '<a href="%s">%s</a>' % (url, title)

    def insert_links(m):
        raw, provider_name, pk = m.groups()
        try:
            pk = int(pk)
            obj = prefetched[provider_name][pk]
        except (ValueError, KeyError):
            return raw
        provider = providers.for_name(provider_name)
        return urlize(obj.get_absolute_url(), provider.get_title(obj))

    if prefetched is None:
        prefetched = get_mentions(text)

    prefetched = dict((provider_name, dict((obj.pk, obj) for obj in objs))
                      for provider_name, objs in prefetched.items())
    return MENTION_PATTERN.sub(insert_links, unicode(text))


def plain_mentions(text):
    return MENTION_PATTERN.sub('\g<title>', text)


def make_mention(obj):
    provider = providers.for_model(obj)
    return '@[%s](%s:%s)' % (provider.get_title(obj), provider.name, obj.pk)


def get_mentions(text):
    mentions = [(type_, pk) for raw, type_, pk in MENTION_PATTERN.findall(unicode(text))]

    by_type = {}
    for type_, pk in mentions:
        by_type.setdefault(type_, set()).add(pk)

    ret = {}
    for provider_name, pks in by_type.items():
        provider = providers.for_name(provider_name)
        ret[provider_name] = provider.get_queryset().filter(pk__in=pks)
    return ret

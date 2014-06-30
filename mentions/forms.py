import uuid

from django import forms
from django.core.urlresolvers import reverse


class MentionTextarea(forms.Textarea):
    """Required: jquery"""
    class Media:
        css = {
            'all': ('css/jquery.mentions.css',)
        }
        js = ('js/jquery.mentions.js',)

    def render(self, name, value, attrs=None):
        extra_attrs = {
            'id': uuid.uuid4().hex,
            'data-source': reverse('mention_complete')
        }
        if attrs:
            extra_attrs.update(attrs)
        return super(MentionTextarea, self).render(name, value, extra_attrs)

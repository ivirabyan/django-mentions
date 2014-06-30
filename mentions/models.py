# coding: utf-8
from functools import partial

from django.db.models.signals import post_save, post_init
from django.db import models
from django.conf import settings

from .forms import MentionTextarea
from .registry import providers
from .utils import get_mentions
from .signals import objects_mentioned


class AddListener(object):
    def __init__(self, field):
        self.field = field
        self.name = '_' + field.name

    def contribute_to_class(self, cls, name):
        register_listener(cls, self.field)


class MentionTextField(models.TextField):
    def __init__(self, *args, **kwargs):
        self.links = kwargs.pop('links', [])
        super(MentionTextField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'widget': MentionTextarea()}
        defaults.update(**kwargs)
        return super(MentionTextField, self).formfield(**defaults)

    def contribute_to_class(self, cls, name):
        super(MentionTextField, self).contribute_to_class(cls, name)
        if not cls._meta.abstract and not cls._meta.swapped:
            register_listener(cls, self)
            # Черствый хак, для того чтобы contribute_to_class вызывался и
            # для дочерних моделей
            cls._meta.add_virtual_field(AddListener(self))


def register_listener(cls, field):
    process = partial(process_mentions, field=field)
    post_save.connect(process, sender=cls, weak=False)
    post_init.connect(partial(preserve_orig_values, field=field),
                      sender=cls, weak=False)


def preserve_orig_values(instance, field, **kwargs):
    setattr(instance, '_%s_initial' % field.name,
            field.value_from_object(instance))


def process_mentions(instance, created, field, **kwargs):
    initial = getattr(instance, '_%s_initial' % field.name)
    text = field.value_from_object(instance)
    if not created and initial == text:
        return

    m2mfields = dict((f.rel.to, f) for f in instance._meta.many_to_many
                     if f.name in field.links)
    for provider_name, objs in get_mentions(text).items():
        try:
            get_extra_mentions = getattr(instance, 'get_%s_mentions' % provider_name)
        except AttributeError:
            pass
        else:
            objs = set(objs) | set(get_extra_mentions())

        model = providers.for_name(provider_name).model
        if model in m2mfields:
            setattr(instance, m2mfields[model].name, objs)
        objects_mentioned.send(mentions=objs, instance=instance, created=created, sender=model)


if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([
        (
            [MentionTextField],
            [],
            {
                #'links': ['links', {}],
            }
        ),
    ], ["^mentions\.models\.MentionTextField"])
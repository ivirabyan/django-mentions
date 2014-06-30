import re
from importlib import import_module

from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.utils.functional import lazy
from django.core import exceptions
from django.conf import settings


class Provider(object):
    model = None

    def __init__(self):
        self.name = re.sub('provider$', '', self.__class__.__name__.lower())

    def get_queryset(self):
        if self.model is None:
            raise ImproperlyConfigured('No model defined')
        return self.model._default_manager.all()

    def get_object(self, pk):
        try:
            return self.get_queryset().get(pk=pk)
        except ObjectDoesNotExist:
            return None

    def search(self, request, term):
        raise NotImplemented

    def get_title(self, obj):
        raise NotImplemented

    def get_image(self, obj):
        return None


class ProviderRegistry(object):
    def __init__(self):
        self.providers = set()
        self.collections = {}

    def register(self, provider, collection='default'):
        provider = provider()
        self.providers.add(provider)
        self.collections.setdefault(collection, set()).add(provider)

    def for_name(self, name):
        return next(p for p in self.providers if p.name == name)

    def for_model(self, model):
        model = model._meta.concrete_model
        return next(p for p in self.providers if p.model == model)

    def get_collection(self, name):
        return self.collections[name]


def _bootstrap():
    _registry = ProviderRegistry()
    MENTIONED_CLASSES = getattr(settings, 'MENTIONS_PROVIDERS', {})
    for collection, path_list in MENTIONED_CLASSES.items():
        for path in path_list:
            try:
                module, classname = path.rsplit('.', 1)
            except ValueError:
                raise exceptions.ImproperlyConfigured('%s isn\'t a module' % path)
            try:
                mod = import_module(module)
            except ImportError, e:
                raise exceptions.ImproperlyConfigured('Error importing class %s: "%s"' % (module, e))
            try:
                cls = getattr(mod, classname)
            except AttributeError:
                raise exceptions.ImproperlyConfigured('Module "%s" does not define a "%s" class' % (module, classname))
            _registry.register(cls, collection)
    return _registry


providers = lazy(_bootstrap, ProviderRegistry)()

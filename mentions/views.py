import json

from django.http import HttpResponse


from .registry import providers


def autocomplete(request):
    term = request.GET.get('term', '')
    collection_name = request.GET.get('mentions', 'default')

    ret = []
    if term:
        try:
            collection = providers.get_collection(collection_name)
        except KeyError:
            collection = providers.get_collection('default')

        for provider in collection:
            objs = provider.search(request, term)
            for obj in objs:
                ret.append({
                    'value': provider.get_title(obj),
                    'image': provider.get_image(obj),
                    'uid': '%s:%s' % (provider.name, obj.pk),
                })

    return HttpResponse(json.dumps(ret), mimetype='application/json')

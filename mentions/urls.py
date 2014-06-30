from django.conf.urls import patterns, url

urlpatterns = patterns('mentions.views',
    url('^autocomplete/$', 'autocomplete', name='mention_complete')
)

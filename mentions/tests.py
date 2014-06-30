import json
from django.test import TestCase
from django.db import models
from django import forms
from django.core.urlresolvers import reverse
from mock import patch

from .models import MentionTextField
from .registry import Provider, ProviderRegistry
from .utils import make_mention
from .helpers import urlize_mentions
from .forms import MentionTextarea


class User(models.Model):
    name = models.CharField(max_length=30)

    def get_absolute_url(self):
        return '/users/%d/' % self.pk


class Post(models.Model):
    text = MentionTextField(links=['users'])

    users = models.ManyToManyField(User)


class UserProvider(Provider):
    model = User

    def get_title(self, obj):
        return obj.name

    def search(self, request, term):
        return self.get_queryset().filter(name__istartswith=term)


providers = ProviderRegistry()
providers.register(UserProvider)


@patch('mentions.utils.providers', providers)
@patch('mentions.models.providers', providers)
@patch('mentions.views.providers', providers)
class MentionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(pk=1, name='Johny')

    def test_filter(self):
        self.text = 'I hate you %s' % make_mention(self.user)
        self.assertEqual(urlize_mentions(self.text),
                         'I hate you <a href="/users/1/">Johny</a>')

    def test_link(self):
        post = Post.objects.create(text=make_mention(self.user))
        self.assertEqual(post.users.get(), self.user)

    def test_widget(self):
        class PostForm(forms.ModelForm):
            class Meta:
                model = Post
        form = PostForm()
        self.assertEqual(form.fields['text'].widget.__class__, MentionTextarea)
        unicode(form.fields['text'])

    def test_widget_render(self):
        MentionTextarea().render(name='text', value='sosiska')

    def test_view(self):
        User.objects.create(name='Kenny')
        response = self.client.get(reverse('mention_complete'), data={'term': 'j'})
        content = json.loads(response.content)
        expected = [{'value': 'Johny', 'image': None, 'uid': 'user:1'}]
        self.assertEqual(content, expected)

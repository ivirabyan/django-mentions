from django.contrib.auth import get_user_model

from .registry import Provider


class UserProvider(Provider):
    model = get_user_model()

    def get_title(self, obj):
        return obj.username

    def search(self, request, term):
        return self.get_queryset().filter(username__istartswith=term)

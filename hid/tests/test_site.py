from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from hid import views


class SiteTest(TestCase):

    def setUp(self):
        self._create_user_and_login()

    def _create_user(self, username, password):
        user, created = User.objects.get_or_create(username=username)
        user.set_password(password)
        user.save()
        return  user

    def _login(self, username, password):
        client = Client()
        assert client.login(username=username, password=password)
        return client

    def _create_user_and_login(self, username='bob', password='bob'):
        self.user = self._create_user(username, password)
        self.client = self._login(username, password)
        self.anon = Client()

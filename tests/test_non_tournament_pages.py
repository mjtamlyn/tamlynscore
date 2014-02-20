from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from . import factories


class BasicPageTest(object):
    url_name = None
    responses = None
    login_required = False

    def setUp(self):
        self.client = Client()

    def login(self):
        user = factories.UserFactory.create()
        logged_in = self.client.login(username=user.username, password=user.raw_password)
        self.assertTrue(logged_in)

    def url_resolver(self):
        return reverse(self.url_name)

    def check_responses(self, url):
        if self.login_required:
            self.login()
        for method, code in self.responses:
            response = getattr(self.client, method)(url)
            self.assertEqual(response.status_code, code)

    def check_login_required(self, url):
        self.client.logout()
        for method, code in self.responses:
            response = getattr(self.client, method)(url)
            self.assertRedirects(response, settings.LOGIN_URL + '?next=' + url)

    def test_basics(self):
        url = self.url_resolver()
        if self.responses:
            self.check_responses(url)
        if self.login_required:
            self.check_login_required(url)


class TestIndex(BasicPageTest, TestCase):
    url_name = 'index'
    responses = (('get', 200),)
    login_required = True


class TestClubList(BasicPageTest, TestCase):
    url_name = 'club_list'
    responses = (('get', 200),)
    login_required = True

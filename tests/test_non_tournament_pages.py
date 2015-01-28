from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from core.models import Archer, Club
from . import factories


class BasicPageTest(object):
    url_name = None
    user = None

    def setUp(self):
        self.client = Client()

    def login(self):
        if self.user is None:
            self.user = factories.UserFactory.create()
        logged_in = self.client.login(username=self.user.username, password=self.user.raw_password)
        self.assertTrue(logged_in)

    def reverse(self):
        return reverse(self.url_name)

    def get_response(self, url=None, data=None, login=True):
        if login:
            self.login()
        if url is None:
            url = self.reverse()
        if data is None:
            data = {}
        return self.client.get(url, data=data)

    def post_response(self, url=None, data=None, login=True):
        if login:
            self.login()
        if url is None:
            url = self.reverse()
        if data is None:
            data = {}
        return self.client.post(url, data=data)

    def test_login_required(self):
        url = self.reverse()
        response = self.get_response(url, login=False)
        self.assertRedirects(response, settings.LOGIN_URL + '?next=' + url)

    def test_get(self):
        response = self.get_response()
        self.assertEqual(response.status_code, 200)


class TestIndex(BasicPageTest, TestCase):
    url_name = 'index'


class TestClubList(BasicPageTest, TestCase):
    url_name = 'club_list'


class TestClubCreate(BasicPageTest, TestCase):
    url_name = 'club_create'

    def test_valid_post(self):
        data = {'name': 'The Most Awesome Archery Club', 'short_name': 'Awesome AC'}
        response = self.post_response(data=data)
        club = Club.objects.get()
        self.assertRedirects(response, club.get_absolute_url())

    def test_valid_post_with_next(self):
        next_url = reverse('index')
        url = '%s?next=%s' % (self.reverse(), next_url)
        data = {'name': 'The Most Awesome Archery Club', 'short_name': 'Awesome AC'}
        response = self.post_response(url=url, data=data)
        self.assertEqual(Club.objects.count(), 1)
        self.assertRedirects(response, next_url)


class TestArcherCreate(BasicPageTest, TestCase):
    url_name = 'archer_create'

    def setUp(self):
        self.club = factories.ClubFactory.create()
        self.bowstyle = factories.BowstyleFactory.create()

    def get_data(self):
        return {
            'name': 'Test Archer',
            'club': self.club.pk,
            'bowstyle': self.bowstyle.pk,
            'gender': 'L',
            'age': 'S',
            'novice': 'N',
        }

    def test_valid_post(self):
        data = self.get_data()
        response = self.post_response(data=data)
        archer = Archer.objects.get()
        self.assertRedirects(response, archer.club.get_absolute_url())

    def test_entry_redirect(self):
        competition = factories.CompetitionFactory.create()
        url = '%s?competition=%s' % (self.reverse(), competition.slug)
        data = self.get_data()
        response = self.post_response(url=url, data=data)
        archer = Archer.objects.get()
        self.assertRedirects(response, reverse('entry_add', kwargs={
            'slug': competition.slug,
            'archer_id': archer.pk,
        }))

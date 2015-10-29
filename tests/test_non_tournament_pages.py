from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.http import urlencode

from core.models import Archer, Club

from . import factories
from .cases import ViewCase, LoggedInViewCase


class TestIndex(ViewCase, TestCase):
    url_name = 'index'

    def test_ok(self):
        response = self.get_response()
        self.assertEqual(response.status_code, 200)


class TestClubList(ViewCase, TestCase):
    url_name = 'club_list'

    def test_ok(self):
        response = self.get_response()
        self.assertEqual(response.status_code, 200)


class TestClubCreate(LoggedInViewCase, TestCase):
    url_name = 'club_create'

    def test_ok(self):
        response = self.get_response()
        self.assertEqual(response.status_code, 200)

    def test_valid_post(self):
        data = {'name': 'The Most Awesome Archery Club', 'short_name': 'Awesome AC'}
        response = self.post_response(data=data)
        club = Club.objects.get()
        self.assertRedirects(response, club.get_absolute_url())

    def test_valid_post_with_next(self):
        next_url = reverse('index')
        get_args = {'next': next_url}
        data = {'name': 'The Most Awesome Archery Club', 'short_name': 'Awesome AC'}
        response = self.post_response(data=data, QUERY_STRING=urlencode(get_args, doseq=True))
        self.assertEqual(Club.objects.count(), 1)
        self.assertRedirects(response, next_url)


class TestArcherCreate(LoggedInViewCase, TestCase):
    url_name = 'archer_create'

    def setUp(self):
        self.club = factories.ClubFactory.create()
        self.bowstyle = factories.BowstyleFactory.create()

    def test_ok(self):
        response = self.get_response()
        self.assertEqual(response.status_code, 200)

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
        self.user = factories.SuperuserFactory.create()
        competition = factories.CompetitionFactory.create()
        get_args = {'competition': competition.slug}
        data = self.get_data()
        response = self.post_response(data=data, QUERY_STRING=urlencode(get_args, doseq=True))
        archer = Archer.objects.get()
        self.assertRedirects(response, reverse('entry_add', kwargs={
            'slug': competition.slug,
            'archer_id': archer.pk,
        }))

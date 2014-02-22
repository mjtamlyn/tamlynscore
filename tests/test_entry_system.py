import unittest

from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse, resolve
from django.test import TestCase, RequestFactory

from entries.forms import EntrySearchForm, EntryCreateForm
from entries.views import EntryList

from . import factories


class LoggedInRequestFactory(RequestFactory):

    def __init__(self, user, **kwargs):
        self.user = user
        return super(LoggedInRequestFactory, self).__init__(**kwargs)

    def request(self, **kwargs):
        request = super(LoggedInRequestFactory, self).request(**kwargs)
        request.user = self.user
        return request


class TestEntryList(TestCase):
    def setUp(self):
        self.competition = factories.CompetitionFactory.create()
        self.user = factories.UserFactory.create()
        self.rf = LoggedInRequestFactory(self.user)

    def test_simple(self):
        view = EntryList.as_view()
        request = self.rf.get('/')
        response = view(request, slug=self.competition.slug)
        self.assertEqual(response.status_code, 200)
        response.render()

    def test_context(self):
        session_round = factories.SessionRoundFactory.create(session__competition=self.competition)
        session_entry = factories.SessionEntryFactory.create(competition_entry__competition=self.competition, session_round=session_round)
        competition_entry = session_entry.competition_entry
        view = EntryList.as_view()
        request = self.rf.get('/')
        response = view(request, slug=self.competition.slug)
        context = response.context_data
        self.assertEqual(context['entries'], [{
            'entry': competition_entry,
            'rounds': [session_entry.session_round.pk],
        }])
        self.assertEqual(context['competition'], self.competition)
        self.assertEqual(context['sessions'], [{
            'session': session_round.session,
            'rounds': [session_round],
        }])
        self.assertIsInstance(context['search_form'], EntrySearchForm)
        self.assertIsInstance(context['new_form'], EntryCreateForm)

    def test_auth(self):
        view = EntryList.as_view()
        request = self.rf.get('/')
        request.user = AnonymousUser()
        response = view(request, slug=self.competition.slug)
        self.assertEqual(response.status_code, 302)

    def test_reversal(self):
        url = reverse('entry_list', kwargs={'slug': self.competition.slug})
        match = resolve(url)
        self.assertEqual(match.func.__name__, 'EntryList')

    @unittest.expectedFailure
    def test_search(self):
        session_round = factories.SessionRoundFactory.create(session__competition=self.competition)
        steve = factories.SessionEntryFactory.create(competition_entry__competition=self.competition, session_round=session_round, competition_entry__archer__name='steve')
        bob = factories.SessionEntryFactory.create(competition_entry__competition=self.competition, session_round=session_round, competition_entry__archer__name='bob', competition_entry__club__name='steventon')
        factories.SessionEntryFactory.create(competition_entry__competition=self.competition, session_round=session_round, competition_entry__archer__name='dave')
        view = EntryList.as_view()
        request = self.rf.get('/', {'search': 'steve'})
        response = view(request, slug=self.competition.slug)
        self.assertEqual(list(response.context_data['object_list']), [steve.competition_entry, bob.competition_entry])

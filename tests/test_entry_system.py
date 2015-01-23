from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse, resolve
from django.test import TestCase, RequestFactory

from entries.forms import ArcherSearchForm, EntryCreateForm
from entries.models import CompetitionEntry
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
        view = EntryList.as_view()
        request = self.rf.get('/')
        response = view(request, slug=self.competition.slug)
        context = response.context_data
        self.assertEqual(context['competition'], self.competition)

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


class TestExistingArcherSingleSession(TestCase):
    """Test the entry flow situation 1:

    Entering an archer already in the system into a competition with a single
    session entry/round, using all their default values.
    """

    def setUp(self):
        self.archer = factories.ArcherFactory.create()
        self.session_round = factories.SessionRoundFactory.create()
        self.competition = self.session_round.session.competition
        self.user = factories.UserFactory.create()
        self.client.login(username=self.user.username, password='password')

    def test_get_search_form(self):
        url = reverse('archer_search', kwargs={'slug': self.competition.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['search_form'], ArcherSearchForm)

    def test_enter_search_term(self):
        url = reverse('archer_search', kwargs={'slug': self.competition.slug})
        data = {'query': self.archer.name}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['search_form'], ArcherSearchForm)
        self.assertSequenceEqual(response.context['archers'], [self.archer])

    def test_select_archer(self):
        url = reverse('entry_add', kwargs={
            'slug': self.competition.slug,
            'archer_id': self.archer.pk,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['archer'], self.archer)
        self.assertIsInstance(response.context['form'], EntryCreateForm)

    def test_submit_entry(self):
        url = reverse('entry_add', kwargs={
            'slug': self.competition.slug,
            'archer_id': self.archer.pk,
        })
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.archer, self.archer)
        self.assertEqual(entry.archer.club, self.archer.club)
        self.assertEqual(entry.archer.bowstyle, self.archer.bowstyle)
        self.assertEqual(entry.sessionentry_set.get().session_round, self.session_round)


class TestMoreSearches(TestCase):

    def setUp(self):
        self.archer = factories.ArcherFactory.create(name='David Longworth', club__name='Oxford Archers')
        self.competition = factories.CompetitionFactory.create()
        self.user = factories.UserFactory.create()
        self.client.login(username=self.user.username, password='password')

    def test_bad_spelling(self):
        url = reverse('archer_search', kwargs={'slug': self.competition.slug})
        data = {'query': 'dave lonworth'}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['search_form'], ArcherSearchForm)
        self.assertSequenceEqual(response.context['archers'], [self.archer])

    def test_club_name(self):
        url = reverse('archer_search', kwargs={'slug': self.competition.slug})
        data = {'query': 'Oxford Archers'}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['search_form'], ArcherSearchForm)
        self.assertSequenceEqual(response.context['archers'], [self.archer])

    def test_bad_club_name(self):
        url = reverse('archer_search', kwargs={'slug': self.competition.slug})
        data = {'query': 'oxford archery club'}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['search_form'], ArcherSearchForm)
        self.assertSequenceEqual(response.context['archers'], [self.archer])

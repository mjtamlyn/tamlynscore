from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse, resolve
from django.test import TestCase, RequestFactory

from core.models import Archer
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
        self.assertEqual(entry.club, self.archer.club)
        self.assertEqual(entry.bowstyle, self.archer.bowstyle)
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


class TestMultiSession(TestCase):

    def setUp(self):
        self.archer = factories.ArcherFactory.create()
        self.competition = factories.CompetitionFactory.create()
        self.session_round = factories.SessionRoundFactory.create(session__competition=self.competition)
        self.session_round_2 = factories.SessionRoundFactory.create(session__competition=self.competition)
        self.user = factories.UserFactory.create()
        self.client.login(username=self.user.username, password='password')

    def test_select_archer(self):
        url = reverse('entry_add', kwargs={
            'slug': self.competition.slug,
            'archer_id': self.archer.pk,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['archer'], self.archer)
        self.assertIsInstance(response.context['form'], EntryCreateForm)
        self.assertTrue('sessions' in response.context['form'].fields)

    def test_single_session(self):
        url = reverse('entry_add', kwargs={
            'slug': self.competition.slug,
            'archer_id': self.archer.pk,
        })
        data = {
            'sessions': [self.session_round.pk],
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.archer, self.archer)
        self.assertEqual(entry.archer.club, self.archer.club)
        self.assertEqual(entry.archer.bowstyle, self.archer.bowstyle)
        self.assertEqual(entry.sessionentry_set.get().session_round, self.session_round)

    def test_both_sessions(self):
        url = reverse('entry_add', kwargs={
            'slug': self.competition.slug,
            'archer_id': self.archer.pk,
        })
        data = {
            'sessions': [self.session_round.pk, self.session_round_2.pk],
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.archer, self.archer)
        self.assertEqual(entry.archer.club, self.archer.club)
        self.assertEqual(entry.archer.bowstyle, self.archer.bowstyle)
        self.assertEqual(entry.sessionentry_set.count(), 2)
        self.assertSequenceEqual(
            entry.sessionentry_set.values_list('session_round_id', flat=True),
            [self.session_round.pk, self.session_round_2.pk],
        )

    def test_no_sessions_fail(self):
        url = reverse('entry_add', kwargs={
            'slug': self.competition.slug,
            'archer_id': self.archer.pk,
        })
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CompetitionEntry.objects.count(), 0)


class TestDifferentEntryDetails(TestCase):

    def setUp(self):
        self.archer = factories.ArcherFactory.create()
        self.competition = factories.CompetitionFactory.create()
        self.session_round = factories.SessionRoundFactory.create(session__competition=self.competition)
        self.user = factories.UserFactory.create()
        self.client.login(username=self.user.username, password='password')

    def test_different_club(self):
        other_club = factories.ClubFactory.create()
        url = reverse('entry_add', kwargs={
            'slug': self.competition.slug,
            'archer_id': self.archer.pk,
        })
        data = {'club': other_club.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.club, other_club)

    def test_different_club_with_update(self):
        other_club = factories.ClubFactory.create()
        url = reverse('entry_add', kwargs={
            'slug': self.competition.slug,
            'archer_id': self.archer.pk,
        })
        data = {
            'club': other_club.pk,
            'update_club': True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.club, other_club)
        archer = Archer.objects.get()
        self.assertEqual(archer.club, other_club)

    def test_different_bowstyle(self):
        other_bowstyle = factories.BowstyleFactory.create()
        url = reverse('entry_add', kwargs={
            'slug': self.competition.slug,
            'archer_id': self.archer.pk,
        })
        data = {'bowstyle': other_bowstyle.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.bowstyle, other_bowstyle)

    def test_different_bowstyle_with_update(self):
        other_bowstyle = factories.BowstyleFactory.create()
        url = reverse('entry_add', kwargs={
            'slug': self.competition.slug,
            'archer_id': self.archer.pk,
        })
        data = {
            'bowstyle': other_bowstyle.pk,
            'update_bowstyle': True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.bowstyle, other_bowstyle)
        archer = Archer.objects.get()
        self.assertEqual(archer.bowstyle, other_bowstyle)

    def test_default_experience(self):
        self.assertEqual(self.archer.novice, 'E')
        self.assertFalse(self.competition.has_novices)
        url = reverse('entry_add', kwargs={
            'slug': self.competition.slug,
            'archer_id': self.archer.pk,
        })
        response = self.client.get(url)
        self.assertNotIn('novice', response.context['form'].fields)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.novice, 'E')

    def test_change_experience(self):
        self.assertEqual(self.archer.novice, 'E')
        self.competition.has_novices = True
        self.competition.save()
        url = reverse('entry_add', kwargs={
            'slug': self.competition.slug,
            'archer_id': self.archer.pk,
        })
        data = {'novice': 'N'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.novice, 'N')

    def test_change_experience_with_update(self):
        self.assertEqual(self.archer.novice, 'E')
        self.competition.has_novices = True
        self.competition.save()
        url = reverse('entry_add', kwargs={
            'slug': self.competition.slug,
            'archer_id': self.archer.pk,
        })
        data = {
            'novice': 'N',
            'update_novice': True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.novice, 'N')
        archer = Archer.objects.get()
        self.assertEqual(archer.novice, 'N')

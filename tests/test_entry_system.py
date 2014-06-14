from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse, resolve
from django.test import TestCase, RequestFactory

from entries.forms import ArcherSearchForm, EntryCreateForm
from entries.models import CompetitionEntry, SessionEntry
from entries.views import EntryList, EntryAdd

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


class TestEntryAdd(TestCase):
    def setUp(self):
        self.competition = factories.CompetitionFactory.create()
        self.user = factories.UserFactory.create()
        self.rf = LoggedInRequestFactory(self.user)

    def test_simple(self):
        view = EntryAdd.as_view()
        request = self.rf.get('/')
        response = view(request, slug=self.competition.slug)
        self.assertEqual(response.status_code, 200)
        response.render()

    def test_context(self):
        view = EntryAdd.as_view()
        request = self.rf.get('/')
        response = view(request, slug=self.competition.slug)
        context = response.context_data
        self.assertIsInstance(context['form'], EntryCreateForm)

    def test_auth(self):
        view = EntryAdd.as_view()
        request = self.rf.get('/')
        request.user = AnonymousUser()
        response = view(request, slug=self.competition.slug)
        self.assertEqual(response.status_code, 302)

    def test_reversal(self):
        url = reverse('entry_add', kwargs={'slug': self.competition.slug})
        match = resolve(url)
        self.assertEqual(match.func.__name__, 'EntryAdd')

    def test_post(self):
        archer = factories.ArcherFactory.create()
        session_round = factories.SessionRoundFactory.create(session__competition=self.competition)
        request = self.rf.post('/', {
            'archer': archer.pk,
            'bowstyle': archer.bowstyle_id,
            'club': archer.club_id,
            'session_%s' % session_round.session_id: session_round.pk,
        })
        view = EntryAdd.as_view()
        response = view(request, slug=self.competition.slug)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)


class TestArcherSearchForm(TestCase):
    def test_search(self):
        steve = factories.ArcherFactory.create(name='steve')
        bob = factories.ArcherFactory.create(name='bob', club__name='steventon')
        factories.ArcherFactory.create(name='dave')
        form = ArcherSearchForm({'query': 'steve'})
        self.assertTrue(form.is_valid())
        self.assertEqual(list(form.get_qs()), [steve, bob])


class TestEntryCreateForm(TestCase):
    def setUp(self):
        self.competition = factories.CompetitionFactory.create()

    def test_simple(self):
        archer = factories.ArcherFactory.create()
        session_round = factories.SessionRoundFactory.create(session__competition=self.competition)
        data = {
            'archer': archer.pk,
            'bowstyle': archer.bowstyle_id,
            'club': archer.club_id,
            'session_%s' % session_round.session.pk: session_round.pk,
        }
        form = EntryCreateForm(competition=self.competition, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        self.assertEqual(SessionEntry.objects.count(), 1)

    def test_fails_with_no_archer(self):
        form = EntryCreateForm(competition=self.competition, data={})
        self.assertFalse(form.is_valid())
        self.assertTrue('archer' in form.errors)

    def test_fails_with_no_sessions(self):
        archer = factories.ArcherFactory.create()
        factories.SessionRoundFactory.create(session__competition=self.competition)
        data = {
            'archer': archer.pk,
        }
        form = EntryCreateForm(competition=self.competition, data=data)
        self.assertFalse(form.is_valid())

    def test_not_all_sessions_required(self):
        archer = factories.ArcherFactory.create()
        session_round = factories.SessionRoundFactory.create(session__competition=self.competition)
        factories.SessionRoundFactory.create(session__competition=self.competition)
        data = {
            'archer': archer.pk,
            'bowstyle': archer.bowstyle_id,
            'club': archer.club_id,
            'session_%s' % session_round.session.pk: session_round.pk,
        }
        form = EntryCreateForm(competition=self.competition, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        self.assertEqual(SessionEntry.objects.count(), 1)

    def test_multiple_sessions(self):
        archer = factories.ArcherFactory.create()
        session_round = factories.SessionRoundFactory.create(session__competition=self.competition)
        session_round_2 = factories.SessionRoundFactory.create(session__competition=self.competition)
        data = {
            'archer': archer.pk,
            'bowstyle': archer.bowstyle_id,
            'club': archer.club_id,
            'session_%s' % session_round.session.pk: session_round.pk,
            'session_%s' % session_round_2.session.pk: session_round_2.pk,
        }
        form = EntryCreateForm(competition=self.competition, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        self.assertEqual(SessionEntry.objects.count(), 2)

    def test_session_fields(self):
        sr1 = factories.SessionRoundFactory.create(session__competition=self.competition)
        sr2 = factories.SessionRoundFactory.create(session=sr1.session)
        sr3 = factories.SessionRoundFactory.create(session__competition=self.competition)
        form = EntryCreateForm(competition=self.competition)
        self.assertEqual(list(form.fields['session_%s' % sr1.session_id].queryset), [sr1, sr2])
        self.assertEqual(list(form.fields['session_%s' % sr3.session_id].queryset), [sr3])

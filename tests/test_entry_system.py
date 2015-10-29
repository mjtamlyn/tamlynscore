from django.core.urlresolvers import reverse
from django.test import TestCase

from core.models import Archer
from entries.forms import ArcherSearchForm, EntryCreateForm
from entries.models import CompetitionEntry

from . import factories
from .cases import ViewCase, LoggedInViewCase


class CompetitionViewCase(ViewCase):
    @classmethod
    def setUpTestData(cls):
        cls.competition = factories.CompetitionFactory.create()
        cls.user = factories.SuperuserFactory.create()

    def get_url_kwargs(self):
        return {'slug': self.competition.slug}


class TestEntryList(CompetitionViewCase, LoggedInViewCase, TestCase):
    url_name = 'entry_list'

    def test_simple(self):
        response = self.get_response()
        self.assertEqual(response.status_code, 200)


class TestArcherSearch(CompetitionViewCase, LoggedInViewCase, TestCase):
    url_name = 'archer_search'

    @classmethod
    def setUpTestData(cls):
        super(TestArcherSearch, cls).setUpTestData()
        cls.archer = factories.ArcherFactory.create(name='David Longworth', club__name='Oxford Archers')
        cls.session_round = factories.SessionRoundFactory.create(session__competition=cls.competition)

    def test_get_search_form(self):
        response = self.get_response()
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['search_form'], ArcherSearchForm)

    def test_enter_search_term(self):
        data = {'query': self.archer.name}
        response = self.get_response(data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['search_form'], ArcherSearchForm)
        self.assertSequenceEqual(response.context['archers'], [self.archer])

    def test_bad_spelling(self):
        data = {'query': 'dave lonworth'}
        response = self.get_response(data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['search_form'], ArcherSearchForm)
        self.assertSequenceEqual(response.context['archers'], [self.archer])

    def test_club_name(self):
        data = {'query': 'Oxford Archers'}
        response = self.get_response(data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['search_form'], ArcherSearchForm)
        self.assertSequenceEqual(response.context['archers'], [self.archer])

    def test_bad_club_name(self):
        data = {'query': 'oxford archery club'}
        response = self.get_response(data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['search_form'], ArcherSearchForm)
        self.assertSequenceEqual(response.context['archers'], [self.archer])


class TestEntryAdd(CompetitionViewCase, LoggedInViewCase, TestCase):
    url_name = 'entry_add'

    @classmethod
    def setUpTestData(cls):
        super(TestEntryAdd, cls).setUpTestData()
        cls.archer = factories.ArcherFactory.create()
        cls.session_round = factories.SessionRoundFactory.create(session__competition=cls.competition)

    def setUp(self):
        self.competition.refresh_from_db()

    def get_url_kwargs(self):
        kwargs = super(TestEntryAdd, self).get_url_kwargs()
        kwargs['archer_id'] = self.archer.pk
        return kwargs

    def test_select_archer(self):
        response = self.get_response()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['archer'], self.archer)
        self.assertIsInstance(response.context['form'], EntryCreateForm)

    def test_submit_entry(self):
        response = self.post_response()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.archer, self.archer)
        self.assertEqual(entry.club, self.archer.club)
        self.assertEqual(entry.bowstyle, self.archer.bowstyle)
        self.assertEqual(entry.sessionentry_set.get().session_round, self.session_round)

    def setup_multisession(self):
        self.session_round_2 = factories.SessionRoundFactory.create(session__competition=self.competition)

    def test_multisession_select_archer(self):
        self.setup_multisession()
        response = self.get_response()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['archer'], self.archer)
        self.assertIsInstance(response.context['form'], EntryCreateForm)
        self.assertTrue('sessions' in response.context['form'].fields)

    def test_single_of_multisession(self):
        self.setup_multisession()
        data = {
            'sessions': [self.session_round.pk],
        }
        response = self.post_response(data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.archer, self.archer)
        self.assertEqual(entry.archer.club, self.archer.club)
        self.assertEqual(entry.archer.bowstyle, self.archer.bowstyle)
        self.assertEqual(entry.sessionentry_set.get().session_round, self.session_round)

    def test_both_sessions(self):
        self.setup_multisession()
        data = {
            'sessions': [self.session_round.pk, self.session_round_2.pk],
        }
        response = self.post_response(data=data)
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
        self.setup_multisession()
        response = self.post_response()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CompetitionEntry.objects.count(), 0)

    def test_different_club(self):
        other_club = factories.ClubFactory.create()
        data = {'club': other_club.pk}
        response = self.post_response(data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.club, other_club)

    def test_different_club_with_update(self):
        other_club = factories.ClubFactory.create()
        data = {
            'club': other_club.pk,
            'update_club': True,
        }
        response = self.post_response(data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.club, other_club)
        archer = Archer.objects.get()
        self.assertEqual(archer.club, other_club)

    def test_different_bowstyle(self):
        other_bowstyle = factories.BowstyleFactory.create()
        data = {'bowstyle': other_bowstyle.pk}
        response = self.post_response(data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.bowstyle, other_bowstyle)

    def test_different_bowstyle_with_update(self):
        other_bowstyle = factories.BowstyleFactory.create()
        data = {
            'bowstyle': other_bowstyle.pk,
            'update_bowstyle': True,
        }
        response = self.post_response(data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.bowstyle, other_bowstyle)
        archer = Archer.objects.get()
        self.assertEqual(archer.bowstyle, other_bowstyle)

    def test_default_experience(self):
        self.assertEqual(self.archer.novice, 'E')
        self.assertFalse(self.competition.has_novices)
        response = self.get_response()
        self.assertNotIn('novice', response.context['form'].fields)
        response = self.post_response()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.novice, 'E')

    def test_uses_archer_experience(self):
        self.archer.novice = 'N'
        self.archer.save()
        self.competition.has_novices = True
        self.competition.save()
        response = self.post_response()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.novice, 'N')

    def test_change_experience(self):
        self.assertEqual(self.archer.novice, 'E')
        self.competition.has_novices = True
        self.competition.save()
        data = {'novice': 'N'}
        response = self.post_response(data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.novice, 'N')

    def test_change_experience_with_update(self):
        self.assertEqual(self.archer.novice, 'E')
        self.competition.has_novices = True
        self.competition.save()
        data = {
            'novice': 'N',
            'update_novice': True,
        }
        response = self.post_response(data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.novice, 'N')
        archer = Archer.objects.get()
        self.assertEqual(archer.novice, 'N')

    def test_default_age(self):
        self.assertEqual(self.archer.age, 'S')
        self.assertFalse(self.competition.has_juniors)
        response = self.get_response()
        self.assertNotIn('age', response.context['form'].fields)
        response = self.post_response()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.age, 'S')

    def test_uses_archer_age(self):
        self.archer.age = 'J'
        self.archer.save()
        self.competition.has_juniors = True
        self.competition.save()
        response = self.post_response()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.age, 'J')

    def test_change_age(self):
        self.assertEqual(self.archer.age, 'S')
        self.competition.has_juniors = True
        self.competition.save()
        data = {'age': 'J'}
        response = self.post_response(data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.age, 'J')

    def test_change_age_with_update(self):
        self.assertEqual(self.archer.age, 'S')
        self.competition.has_juniors = True
        self.competition.save()
        data = {
            'age': 'J',
            'update_age': True,
        }
        response = self.post_response(data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CompetitionEntry.objects.count(), 1)
        entry = CompetitionEntry.objects.get()
        self.assertEqual(entry.age, 'J')
        archer = Archer.objects.get()
        self.assertEqual(archer.age, 'J')


class TestEntryDelete(CompetitionViewCase, LoggedInViewCase, TestCase):
    url_name = 'entry_delete'

    @classmethod
    def setUpTestData(cls):
        super(TestEntryDelete, cls).setUpTestData()
        cls.entry = factories.CompetitionEntryFactory.create(competition=cls.competition)

    def get_url_kwargs(self):
        kwargs = super(TestEntryDelete, self).get_url_kwargs()
        kwargs['entry_id'] = self.entry.pk
        return kwargs

    def test_get(self):
        response = self.get_response()
        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        response = self.post_response()
        success_url = reverse('entry_list', kwargs={'slug': self.competition.slug})
        self.assertRedirects(response, success_url)
        self.assertEqual(CompetitionEntry.objects.count(), 0)

import datetime

from django.test import TestCase, RequestFactory
from django.utils import timezone

from core import models as core_models
from entries.forms import NewEntryForm
from entries import models as entries_models
from entries.views import EntryList

from . import factories


class TestNewEntryForm(TestCase):
    def test_session_fields_exist(self):
        session_round = factories.SessionRoundFactory.create()
        competition = session_round.session.competition
        form = NewEntryForm(competition=competition)
        self.assertEqual(len(form.session_fields), 1)
        self.assertSequenceEqual(form.fields['session-0'].queryset, [session_round])

    def test_session_fields_grouped_correctly(self):
        start = timezone.now()
        session_round = factories.SessionRoundFactory.create(session__start=start)
        competition = session_round.session.competition
        session_round_2 = factories.SessionRoundFactory.create(session__competition=competition, session__start=start + datetime.timedelta(hours=1))
        session_round_3 = factories.SessionRoundFactory.create(session=session_round.session)
        form = NewEntryForm(competition=competition)
        self.assertEqual(len(form.session_fields), 2)
        self.assertSequenceEqual(form.fields['session-0'].queryset, [session_round, session_round_3])
        self.assertSequenceEqual(form.fields['session-1'].queryset, [session_round_2])

    def test_basic_data_validation(self):
        session_round = factories.SessionRoundFactory.create()
        competition = session_round.session.competition
        club = factories.ClubFactory.create()
        bowstyle = factories.BowstyleFactory.create()
        data = {
            'session-0': session_round.pk,
            'club_0': club.pk,
            'bowstyle': bowstyle.pk,
            'archer_1': 'New',
            'gender': 'G',
            'novice': 'E',
            'age': 'S',
        }
        form = NewEntryForm(data=data, competition=competition)
        self.assertTrue(form.is_valid(), msg=dict(form.errors))

    def test_no_sessions_validation_error(self):
        session_round = factories.SessionRoundFactory.create()
        competition = session_round.session.competition
        club = factories.ClubFactory.create()
        bowstyle = factories.BowstyleFactory.create()
        data = {
            'club_0': club.pk,
            'bowstyle': bowstyle.pk,
            'archer_1': 'New',
            'gender': 'G',
            'novice': 'E',
            'age': 'S',
        }
        form = NewEntryForm(data=data, competition=competition)
        self.assertFalse(form.is_valid())

    def test_saving_existing_archer(self):
        session_round = factories.SessionRoundFactory.create()
        competition = session_round.session.competition
        archer = factories.ArcherFactory.create()
        data = {
            'session-0': session_round.pk,
            'club_0': archer.club.pk,
            'bowstyle': archer.bowstyle.pk,
            'archer_0': archer.pk,
            'gender': 'G',
            'novice': 'E',
            'age': 'S',
        }
        form = NewEntryForm(data=data, competition=competition)
        form.full_clean()
        form.save()
        self.assertEqual(entries_models.CompetitionEntry.objects.count(), 1)
        entry = entries_models.CompetitionEntry.objects.get()
        self.assertEqual(entry.archer, archer)
        self.assertEqual(entries_models.SessionEntry.objects.count(), 1)
        session_entry = entries_models.SessionEntry.objects.get()
        self.assertEqual(session_entry.competition_entry, entry)

    def test_saving_new_archer(self):
        session_round = factories.SessionRoundFactory.create()
        competition = session_round.session.competition
        club = factories.ClubFactory.create()
        bowstyle = factories.BowstyleFactory.create()
        data = {
            'session-0': session_round.pk,
            'club_0': club.pk,
            'bowstyle': bowstyle.pk,
            'archer_1': 'bob',
            'gender': 'G',
            'novice': 'E',
            'age': 'S',
        }
        form = NewEntryForm(data=data, competition=competition)
        form.full_clean()
        form.save()
        self.assertEqual(entries_models.CompetitionEntry.objects.count(), 1)
        entry = entries_models.CompetitionEntry.objects.get()
        self.assertEqual(core_models.Archer.objects.count(), 1)
        archer = core_models.Archer.objects.get()
        self.assertEqual(entry.archer, archer)
        self.assertEqual(archer.name, 'bob')
        self.assertEqual(archer.club, club)
        self.assertEqual(archer.bowstyle, bowstyle)
        self.assertEqual(archer.gender, 'G')
        self.assertEqual(archer.novice, 'E')
        self.assertEqual(archer.age, 'S')

    def test_saving_new_club(self):
        session_round = factories.SessionRoundFactory.create()
        competition = session_round.session.competition
        archer = factories.ArcherFactory.create()
        data = {
            'session-0': session_round.pk,
            'club_1': 'OA',
            'bowstyle': archer.bowstyle.pk,
            'archer_0': archer.pk,
            'gender': 'G',
            'novice': 'E',
            'age': 'S',
        }
        form = NewEntryForm(data=data, competition=competition)
        form.full_clean()
        form.save()
        self.assertEqual(entries_models.CompetitionEntry.objects.count(), 1)
        # Should be 3 clubs:
        #   host club
        #   archer's club
        #   new club
        self.assertEqual(core_models.Club.objects.count(), 3)
        core_models.Club.objects.get(name='OA')


class TestEntryView(TestCase):
    def test_getting_view(self):
        competition = factories.CompetitionFactory.create()
        request = RequestFactory().get('/')
        request.user = factories.UserFactory.create()
        view = EntryList.as_view()
        response = view(request, slug=competition.slug)
        self.assertEqual(response.status_code, 200)

import datetime

from django.test import TestCase

from entries.forms import CompetitionForm
from entries.models import Competition

from .factories import (
    CompetitionFactory, ResultsModeFactory, RoundFactory, SessionRoundFactory,
    TournamentFactory
)


class TestCompetitionForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rnd = RoundFactory.create()

    def simple_data(self):
        return {
            'full_name': 'Test event archery championships',
            'short_name': 'Test event',
            'date': '2015-01-01',

            'team_size': 4,
            'archers_per_target': 4,
            'scoring_system': 'F',
            'arrows_entered_per_end': 12,
            'session_1_rounds': [self.rnd.pk],
            'session_1_time': '2015-01-01 09:00:00',

            'result_modes': ['by-round'],
        }

    def assert_shoot_fields(self, competition, data):
        self.assertEqual(competition.tournament.full_name, data['full_name'])
        self.assertEqual(competition.tournament.short_name, data['short_name'])
        self.assertEqual(competition.date, datetime.date(2015, 1, 1))
        self.assertEqual(competition.date, datetime.date(2015, 1, 1))

    def assert_session_fields(self, competition, data):
        self.assertEqual(competition.session_set.count(), 1)
        session = competition.session_set.get()
        self.assertEqual(session.start, datetime.datetime(2015, 1, 1, 9))
        self.assertEqual(session.archers_per_target, data['archers_per_target'])
        self.assertEqual(session.scoring_system, data['scoring_system'])
        self.assertEqual(session.arrows_entered_per_end, data['arrows_entered_per_end'])
        self.assertSequenceEqual(session.sessionround_set.values_list('shot_round', flat=True), [self.rnd.pk])

    def assert_result_mode_fields(self, competition, data):
        result_modes = {rm.mode for rm in competition.result_modes.all()}
        self.assertEqual(result_modes, {'by-round'})

    def test_initial_minimal(self):
        competition = CompetitionFactory.create()
        session_round = SessionRoundFactory.create(session__competition=competition)
        result_mode = ResultsModeFactory.create(competition=competition)
        form = CompetitionForm(instance=competition)
        self.assertEqual(form.initial, {
            'full_name': competition.tournament.full_name,
            'short_name': competition.tournament.short_name,
            'date': competition.date,
            'end_date': competition.end_date,

            'archers_per_target': session_round.session.archers_per_target,
            'scoring_system': session_round.session.scoring_system,
            'arrows_entered_per_end': session_round.session.arrows_entered_per_end,
            'session_1_time': session_round.session.start,
            'session_1_rounds': [session_round.shot_round_id],

            'result_modes': [result_mode.mode],

            'has_guests': False,
            'has_novices': False,
            'has_juniors': False,
            'has_wa_age_groups': False,
            'has_agb_age_groups': False,
            'exclude_later_shoots': False,
            'team_size': 4,
            'allow_incomplete_teams': True,
            'combine_rounds_for_team_scores': False,
            'force_mixed_teams': False,
            'split_gender_teams': False,
            'use_county_teams': False,
            'strict_b_teams': False,
            'strict_c_teams': False,
            'novice_team_size': None,
            'novices_in_experienced_individual': False,
            'novices_in_experienced_teams': False,
            'compound_team_size': None,
            'junior_team_size': None,
        })
        saving_form = CompetitionForm(instance=competition, data=form.initial)
        self.assertTrue(saving_form.is_valid(), saving_form.errors.as_json())
        self.assertEqual(competition.session_set.get().sessionround_set.get(), session_round)
        self.assertEqual(competition.result_modes.get(), result_mode)

    def test_simple_create(self):
        data = self.simple_data()
        form = CompetitionForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        form.save()
        competition = Competition.objects.get()
        self.assert_shoot_fields(competition, data)
        self.assert_session_fields(competition, data)
        self.assert_result_mode_fields(competition, data)

    def test_simple_update(self):
        competition = CompetitionFactory.create()
        SessionRoundFactory.create(session__competition=competition, shot_round=self.rnd)
        ResultsModeFactory.create(competition=competition)
        data = self.simple_data()
        form = CompetitionForm(instance=competition, data=data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        form.save()
        competition.refresh_from_db()
        self.assert_shoot_fields(competition, data)
        self.assert_session_fields(competition, data)
        self.assert_result_mode_fields(competition, data)

    def test_existing_tournament(self):
        tournament = TournamentFactory()
        data = self.simple_data()
        data['full_name'] = tournament.full_name
        form = CompetitionForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        form.save()
        competition = Competition.objects.get()
        self.assertEqual(competition.tournament, tournament)

    def multiple_sessions_on_create(self):
        data = self.simple_data()
        data.update({
            'session_2_time': '2015-01-01 12:00:00',
            'session_2_rounds': [self.rnd.pk],
        })
        form = CompetitionForm(data=data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        form.save()
        competition = Competition.objects.get()
        self.assertEqual(competition.session_set.count(), 2)
        sessions = competition.session_set.all()
        self.assertEqual(sessions[0].start, datetime.datetime(2015, 1, 1, 9))
        self.assertEqual(sessions[1].start, datetime.datetime(2015, 1, 1, 12))
        for session in sessions:
            self.assertEqual(session.archers_per_target, data['archers_per_target'])
            self.assertEqual(session.scoring_system, data['scoring_system'])
            self.assertEqual(session.arrows_entered_per_end, data['arrows_entered_per_end'])
            self.assertSequenceEqual(session.sessionround_set.values_list('shot_round', flat=True), [self.rnd.pk])

    def test_session_add(self):
        competition = CompetitionFactory.create()
        SessionRoundFactory.create(session__competition=competition, session__start=datetime.datetime(2015, 1, 1, 9), shot_round=self.rnd)
        ResultsModeFactory.create(competition=competition)
        form = CompetitionForm(instance=competition)
        data = form.initial
        data.update({
            'session_2_time': '2015-01-01 12:00:00',
            'session_2_rounds': [self.rnd.pk],
        })
        form = CompetitionForm(instance=competition, data=data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        form.save()
        self.assertEqual(competition.session_set.count(), 2)
        sessions = competition.session_set.all()
        self.assertEqual(sessions[0].start, datetime.datetime(2015, 1, 1, 9))
        self.assertEqual(sessions[1].start, datetime.datetime(2015, 1, 1, 12))
        for session in sessions:
            self.assertEqual(session.archers_per_target, data['archers_per_target'])
            self.assertEqual(session.scoring_system, data['scoring_system'])
            self.assertEqual(session.arrows_entered_per_end, data['arrows_entered_per_end'])
            self.assertSequenceEqual(session.sessionround_set.values_list('shot_round', flat=True), [self.rnd.pk])

    def test_session_delete(self):
        competition = CompetitionFactory.create()
        SessionRoundFactory.create(session__competition=competition, session__start=datetime.datetime(2015, 1, 1, 9), shot_round=self.rnd)
        SessionRoundFactory.create(session__competition=competition, session__start=datetime.datetime(2015, 1, 1, 12), shot_round=self.rnd)
        ResultsModeFactory.create(competition=competition)
        form = CompetitionForm(instance=competition)
        data = form.initial
        data.pop('session_2_time')
        data.pop('session_2_rounds')
        form = CompetitionForm(instance=competition, data=data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        form.save()
        competition.refresh_from_db()
        self.assert_session_fields(competition, data)

    def test_session_rounds_change(self):
        competition = CompetitionFactory.create()
        SessionRoundFactory.create(session__competition=competition, session__start=datetime.datetime(2015, 1, 1, 9), shot_round=self.rnd)
        ResultsModeFactory.create(competition=competition)
        new_round = RoundFactory.create()
        form = CompetitionForm(instance=competition)
        data = form.initial
        data['session_1_rounds'] = [new_round.pk]
        form = CompetitionForm(instance=competition, data=data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        form.save()
        session = competition.session_set.get()
        self.assertSequenceEqual(session.sessionround_set.values_list('shot_round', flat=True), [new_round.pk])

    def test_session_fields_change(self):
        competition = CompetitionFactory.create()
        SessionRoundFactory.create(session__competition=competition, session__start=datetime.datetime(2015, 1, 1, 9), shot_round=self.rnd)
        ResultsModeFactory.create(competition=competition)
        form = CompetitionForm(instance=competition)
        data = form.initial
        data['archers_per_target'] = 2
        form = CompetitionForm(instance=competition, data=data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        form.save()
        session = competition.session_set.get()
        self.assertEqual(session.archers_per_target, 2)

    def test_session_cross_field_validation(self):
        data = {
            'session_1_time': '2015-01-01 09:00:00',
            'session_1_rounds': [self.rnd.pk],
            'session_2_time': '2015-01-01 12:00:00',
            'session_2_rounds': [],
            'session_3_time': None,
            'session_3_rounds': [self.rnd.pk],
        }
        form = CompetitionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('session_2_time', code='session_match'))
        self.assertTrue(form.has_error('session_3_time', code='session_match'))

    def test_sessions_must_be_in_time_order(self):
        data = {
            'session_1_time': '2015-01-01 15:00:00',
            'session_1_rounds': [self.rnd.pk],
            'session_2_time': '2015-01-01 12:00:00',
            'session_2_rounds': [self.rnd.pk],
        }
        form = CompetitionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('session_1_time', code='session_order'))

    def test_sessions_must_not_have_gaps(self):
        data = {
            'session_1_time': '2015-01-01 15:00:00',
            'session_1_rounds': [self.rnd.pk],
            'session_3_time': '2015-01-01 12:00:00',
            'session_3_rounds': [self.rnd.pk],
        }
        form = CompetitionForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('session_1_time', code='session_order'))

    def test_result_modes_add(self):
        competition = CompetitionFactory.create()
        SessionRoundFactory.create(session__competition=competition, session__start=datetime.datetime(2015, 1, 1, 9), shot_round=self.rnd)
        ResultsModeFactory.create(competition=competition, mode='by-round')
        form = CompetitionForm(instance=competition)
        data = form.initial
        data.update({
            'result_modes': ['by-round', 'by-session'],
        })
        form = CompetitionForm(instance=competition, data=data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        form.save()
        result_modes = {rm.mode for rm in competition.result_modes.all()}
        self.assertEqual(result_modes, {'by-round', 'by-session'})

    def test_result_modes_remove(self):
        competition = CompetitionFactory.create()
        SessionRoundFactory.create(session__competition=competition, session__start=datetime.datetime(2015, 1, 1, 9), shot_round=self.rnd)
        ResultsModeFactory.create(competition=competition, mode='by-round')
        ResultsModeFactory.create(competition=competition, mode='by-session')
        form = CompetitionForm(instance=competition)
        data = form.initial
        data.update({
            'result_modes': ['by-round'],
        })
        form = CompetitionForm(instance=competition, data=data)
        self.assertTrue(form.is_valid(), form.errors.as_json())
        form.save()
        result_modes = {rm.mode for rm in competition.result_modes.all()}
        self.assertEqual(result_modes, {'by-round'})

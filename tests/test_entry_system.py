import datetime

from django.test import TestCase
from django.utils import timezone

from entries.forms import NewEntryForm

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

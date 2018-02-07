from django.utils import timezone

from core import models as core_models
from entries import models as entries_models
from scores.result_modes import ByRound

import factory
from factory import fuzzy


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = core_models.User
    email = factory.Sequence(lambda n: 'user-{0}@example.com'.format(n).lower())

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        email = kwargs.pop('email')
        password = kwargs.pop('password', 'password')
        manager = cls._get_manager(model_class)
        user = manager.create_user(email=email, password=password)
        user.plain_password = password
        if kwargs:
            for k, v in kwargs.items():
                setattr(user, k, v)
            user.save()
        return user


class SuperuserFactory(UserFactory):
    is_superuser = True


class BowstyleFactory(factory.DjangoModelFactory):
    class Meta:
        model = core_models.Bowstyle
    name = factory.Sequence(lambda n: 'Bowstyle %s' % n)


class ClubFactory(factory.DjangoModelFactory):
    class Meta:
        model = core_models.Club
    name = factory.Sequence(lambda n: 'Club %s Company of Archers' % n)
    short_name = factory.Sequence(lambda n: 'Club %s' % n)
    slug = factory.Sequence(lambda n: 'club-%s' % n)


class ArcherFactory(factory.DjangoModelFactory):
    class Meta:
        model = core_models.Archer
    name = fuzzy.FuzzyText(prefix='Archer ')
    club = factory.SubFactory(ClubFactory)
    bowstyle = factory.SubFactory(BowstyleFactory)


class TournamentFactory(factory.DjangoModelFactory):
    class Meta:
        model = entries_models.Tournament
    full_name = factory.Sequence(lambda n: 'Tournament %s Archery Championship' % n)
    short_name = factory.Sequence(lambda n: 'Tournament %s' % n)
    host_club = factory.SubFactory(ClubFactory)


class CompetitionFactory(factory.DjangoModelFactory):
    class Meta:
        model = entries_models.Competition
    tournament = factory.SubFactory(TournamentFactory)
    date = timezone.now().date()
    slug = factory.Sequence(lambda n: 'competition-%s' % n)


class SessionFactory(factory.DjangoModelFactory):
    class Meta:
        model = entries_models.Session
    competition = factory.SubFactory(CompetitionFactory)
    start = timezone.now()
    archers_per_target = 4
    scoring_system = entries_models.SCORING_FULL


class RoundFactory(factory.DjangoModelFactory):
    class Meta:
        model = core_models.Round
    name = factory.Sequence(lambda n: 'Round %s' % n)


class SessionRoundFactory(factory.DjangoModelFactory):
    class Meta:
        model = entries_models.SessionRound
    session = factory.SubFactory(SessionFactory)
    shot_round = factory.SubFactory(RoundFactory)


class CompetitionEntryFactory(factory.DjangoModelFactory):
    class Meta:
        model = entries_models.CompetitionEntry
    competition = factory.SubFactory(CompetitionFactory)
    archer = factory.SubFactory(ArcherFactory)
    club = factory.SubFactory(ClubFactory)
    bowstyle = factory.SubFactory(BowstyleFactory)
    age = 'S'
    novice = 'E'


class SessionEntryFactory(factory.DjangoModelFactory):
    class Meta:
        model = entries_models.SessionEntry
    competition_entry = factory.SubFactory(CompetitionEntryFactory)
    session_round = factory.SubFactory(SessionRoundFactory)


class ResultsModeFactory(factory.DjangoModelFactory):
    class Meta:
        model = entries_models.ResultsMode
    competition = factory.SubFactory(CompetitionFactory)
    mode = ByRound().slug

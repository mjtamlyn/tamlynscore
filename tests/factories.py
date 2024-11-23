from django.utils import timezone

import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from core import models as core_models
from entries import models as entries_models
from olympic import models as olympic_models
from scores.result_modes import ByRound


class UserFactory(DjangoModelFactory):
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


class BowstyleFactory(DjangoModelFactory):
    class Meta:
        model = core_models.Bowstyle
    name = factory.Sequence(lambda n: 'Bowstyle %s' % n)


class ClubFactory(DjangoModelFactory):
    class Meta:
        model = core_models.Club
    name = factory.Sequence(lambda n: 'Club %s Company of Archers' % n)
    short_name = factory.Sequence(lambda n: 'Club %s' % n)
    slug = factory.Sequence(lambda n: 'club-%s' % n)


class ArcherFactory(DjangoModelFactory):
    class Meta:
        model = core_models.Archer
    name = fuzzy.FuzzyText(prefix='Archer ')
    club = factory.SubFactory(ClubFactory)
    bowstyle = factory.SubFactory(BowstyleFactory)


class TournamentFactory(DjangoModelFactory):
    class Meta:
        model = entries_models.Tournament
    full_name = factory.Sequence(lambda n: 'Tournament %s Archery Championship' % n)
    short_name = factory.Sequence(lambda n: 'Tournament %s' % n)
    host_club = factory.SubFactory(ClubFactory)


class CompetitionFactory(DjangoModelFactory):
    class Meta:
        model = entries_models.Competition
    tournament = factory.SubFactory(TournamentFactory)
    date = timezone.now().date()
    slug = factory.Sequence(lambda n: 'competition-%s' % n)


class SessionFactory(DjangoModelFactory):
    class Meta:
        model = entries_models.Session
    competition = factory.SubFactory(CompetitionFactory)
    start = timezone.now()
    archers_per_target = 4
    scoring_system = entries_models.SCORING_FULL


class RoundFactory(DjangoModelFactory):
    class Meta:
        model = core_models.Round
    name = factory.Sequence(lambda n: 'Round %s' % n)


class SessionRoundFactory(DjangoModelFactory):
    class Meta:
        model = entries_models.SessionRound
    session = factory.SubFactory(SessionFactory)
    shot_round = factory.SubFactory(RoundFactory)


class CompetitionEntryFactory(DjangoModelFactory):
    class Meta:
        model = entries_models.CompetitionEntry
    competition = factory.SubFactory(CompetitionFactory)
    archer = factory.SubFactory(ArcherFactory)
    club = factory.SubFactory(ClubFactory)
    bowstyle = factory.SubFactory(BowstyleFactory)
    age = 'S'
    novice = 'E'


class SessionEntryFactory(DjangoModelFactory):
    class Meta:
        model = entries_models.SessionEntry
    competition_entry = factory.SubFactory(CompetitionEntryFactory)
    session_round = factory.SubFactory(SessionRoundFactory)


class ResultsModeFactory(DjangoModelFactory):
    class Meta:
        model = entries_models.ResultsMode
    competition = factory.SubFactory(CompetitionFactory)
    mode = ByRound().slug


class OlympicRoundFactory(DjangoModelFactory):
    class Meta:
        model = olympic_models.OlympicRound
    # By default makes individual set-system matches at 18m
    distance = '18'
    match_type = 'T'
    team_type = ''


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = olympic_models.Category

    @factory.post_generation
    def bowstyles(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.bowstyles.add(*extracted)


class OlympicSessionRoundFactory(DjangoModelFactory):
    class Meta:
        model = olympic_models.OlympicSessionRound
    session = factory.SubFactory(SessionFactory)
    shot_round = factory.SubFactory(OlympicRoundFactory)
    category = factory.SubFactory(CategoryFactory)
    exclude_ranking_rounds = False
    cut = None


class MatchFactory(DjangoModelFactory):
    class Meta:
        model = olympic_models.Match
    session_round = factory.SubFactory(OlympicSessionRoundFactory)
    target = 1
    target_2 = None
    level = 1
    match = 1
    timing = 1

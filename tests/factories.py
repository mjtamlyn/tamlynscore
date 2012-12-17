from django.contrib.auth.models import User
from django.utils import timezone

from core import models as core_models
from entries import models as entries_models

import factory


class UserFactory(factory.Factory):
    FACTORY_FOR = User
    first_name = factory.Sequence(lambda n: 'Firstname {0}'.format(n))
    last_name = factory.Sequence(lambda n: 'Lastname {0}'.format(n))
    username = factory.Sequence(lambda n: 'user-{0}'.format(n).lower())
    email = factory.LazyAttribute(lambda a: '{0}@example.com'.format(a.username).lower())

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', 'password')
        user = super(UserFactory, cls)._prepare(create=False, **kwargs)
        user.set_password(password)
        user.raw_password = password
        if create:
            user.save()
        return user


class ClubFactory(factory.Factory):
    FACTORY_FOR = core_models.Club


class TournamentFactory(factory.Factory):
    FACTORY_FOR = entries_models.Tournament
    host_club = factory.SubFactory(ClubFactory)


class CompetitionFactory(factory.Factory):
    FACTORY_FOR = entries_models.Competition
    tournament = factory.SubFactory(TournamentFactory)
    date = timezone.now().date()


class SessionFactory(factory.Factory):
    FACTORY_FOR = entries_models.Session
    competition = factory.SubFactory(CompetitionFactory)
    start = timezone.now()
    archers_per_target = 4


class RoundFactory(factory.Factory):
    FACTORY_FOR = core_models.Round
    name = factory.Sequence(lambda n: 'Name-%s' % n)


class SessionRoundFactory(factory.Factory):
    FACTORY_FOR = entries_models.SessionRound
    session = factory.SubFactory(SessionFactory)
    shot_round = factory.SubFactory(RoundFactory)

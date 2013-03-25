from django.core.exceptions import ImproperlyConfigured
from django.utils.datastructures import SortedDict


class ScoreMock(object):
    def __init__(self, **kwargs):
        kwargs.setdefault('retired', False)
        kwargs.setdefault('disqualified', False)
        kwargs.setdefault('team', None)
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def guest(self):
        return not self.team and self.target.session_entry.competition_entry.guest

    @property
    def is_team(self):
        return bool(self.team)


class BaseResultMode(object):
    slug = ''
    name = ''

    def __unicode__(self):
        return self.name

    def get_results(self, competition, scores, leaderboard=False):
        raise ImproperlyConfigured('Subclasses must implement get_results')

    def sort_results(self, scores):
        return sorted(scores, key=lambda s: (s.score, s.golds, s.xs, s.hits), reverse=True)


class BySession(BaseResultMode):
    slug = 'by-session'
    name = 'By session'


class ByRound(BaseResultMode):
    slug = 'by-round'
    name = 'By round'

    def get_results(self, competition, scores, leaderboard=False):
        """Get the results for each category, by round.

        Strategy:
        - find all the rounds shot
        - order by the first session they're shot in
        - go through scores, adding to each category specific sets
            - here respect competition options - novices, juniors, second rounds etc.
        """
        self.leaderboard = leaderboard
        rounds = self.get_rounds(competition)
        return SortedDict((round, self.get_round_results(competition, round, scores)) for round in rounds)

    def get_rounds(self, competition):
        from entries.models import SessionRound

        session_rounds = SessionRound.objects.filter(session__competition=competition).order_by('session__start')
        rounds = []
        for round in session_rounds:
            if round.shot_round not in rounds:
                rounds.append(round.shot_round)
        return rounds

    def get_round_results(self, competition, round, scores):
        results = SortedDict()
        for score in scores:
            session_entry = score.target.session_entry
            if session_entry.session_round.shot_round.id is not round.id:
                continue
            if competition.exclude_later_shoots and session_entry.index > 1:
                continue
            category = session_entry.competition_entry.category()
            if category not in results:
                results[category] = []
            if not self.leaderboard and score.score == 0:
                score = ScoreMock(
                    target=score.target,
                    score='DNS',
                    hits='',
                    golds='',
                    xs='',
                    disqualified=False,
                    retired=False,
                )
            results[category].append(score)
        return results


class DoubleRound(BaseResultMode):
    slug = 'double-round'
    name = 'Double round'

    def get_results(self, competition, scores, leaderboard=False):
        """Get the results for each category, by round.

        Strategy:
        - find all the rounds shot
        - order by the first session they're shot in
        - go through scores, adding to each category specific sets
        - need to add a quacking score object which is the double
        """
        self.leaderboard = leaderboard
        rounds = self.get_rounds(competition)
        return SortedDict((round, self.get_round_results(competition, round, scores)) for round in rounds)

    def get_rounds(self, competition):
        from entries.models import SessionRound

        session_rounds = SessionRound.objects.filter(session__competition=competition).order_by('session__start')
        rounds = []
        for round in session_rounds:
            if round.shot_round not in rounds:
                rounds.append(round.shot_round)
        return rounds

    def get_round_results(self, competition, round, scores):
        results = SortedDict()
        for score in scores:
            session_entry = score.target.session_entry
            if session_entry.session_round.shot_round.id is not round.id:
                continue
            category = session_entry.competition_entry.category()
            if category not in results:
                results[category] = {}
            if session_entry.competition_entry not in results[category]:
                results[category][session_entry.competition_entry] = []
            results[category][session_entry.competition_entry].append(score)
        for category, scores in results.items():
            for entry in scores.keys():
                if len(scores[entry]) < 2:
                    scores.pop(entry)
            if not scores:
                results.pop(category)
                continue
            for entry in scores:
                scores[entry] = sorted(scores[entry], key=lambda s: s.target.session_entry.session_round.session.start)[:2]
            new_scores = [ScoreMock(
                    disqualified=any(s.disqualified for s in sub_scores),
                    retired=any(s.disqualified for s in sub_scores),
                    target=sub_scores[0].target,
                    score=sum(s.score for s in sub_scores),
                    hits=sum(s.hits for s in sub_scores),
                    golds=sum(s.golds for s in sub_scores),
                    xs=sum(s.xs for s in sub_scores),
            ) for entry, sub_scores in scores.items()]
            if not self.leaderboard:
                new_scores = filter(lambda s: s.score > 0, new_scores)
            results[category] = self.sort_results(new_scores)
        return results


class Team(BaseResultMode):
    slug = 'team'
    name = 'Teams'

    def get_results(self, competition, scores, leaderboard=False):
        """
        Strategy:
        - split by team
            - find the top scores in each team
            - filter out incomplete teams
            - aggregate and order
        - repeat for each team type
        """
        clubs = {}
        # TODO: handle cross-rounds
        round = None
        for score in scores:
            if not leaderboard and not score.score:
                continue
            session_entry = score.target.session_entry
            if round is None:
                round = session_entry.session_round.shot_round
            club = session_entry.competition_entry.club
            if session_entry.index > 1 or score.disqualified or score.retired:
                continue
            if club not in clubs:
                clubs[club] = []
            clubs[club].append(score)
        results = SortedDict()
        for type in self.get_team_types(competition):
            results[type] = self.get_team_scores(competition, clubs, type)
        return {round: results}

    def get_team_types(self, competition):
        return ['Non-compound', 'Compound', 'Novice']

    def get_team_scores(self, competition, clubs, type):
        club_results = []
        for club, club_scores in clubs.items():
            club_scores = [s for s in club_scores if self.is_valid_for_type(s, type)]
            club_scores = sorted(club_scores, key = lambda s: (s.score, s.golds, s.xs, s.hits), reverse=True)[:competition.team_size]
            if len(club_scores) < competition.team_size:
                continue
            team = ScoreMock(
                score=sum(s.score for s in club_scores),
                hits=sum(s.hits for s in club_scores),
                golds=sum(s.golds for s in club_scores),
                xs=sum(s.xs for s in club_scores),
                club=club,
                team=club_scores,
            )
            club_results.append((club, team))
        return self.sort_results([c[1] for c in club_results])

    def is_valid_for_type(self, score, type):
        if type == 'Non-compound':
            return not score.target.session_entry.competition_entry.bowstyle.name == 'Compound'
        if type == 'Compound':
            return score.target.session_entry.competition_entry.bowstyle.name == 'Compound'
        if type == 'Novice':
            return not score.target.session_entry.competition_entry.bowstyle.name == 'Compound' and score.target.session_entry.competition_entry.novice == 'N'


def get_result_modes():
    modes = BaseResultMode.__subclasses__()
    return [(mode.slug, mode.name) for mode in modes]


def get_mode(slug):
    modes = BaseResultMode.__subclasses__()
    try: 
        return [mode() for mode in modes if mode.slug == slug][0]
    except IndexError:
        return None


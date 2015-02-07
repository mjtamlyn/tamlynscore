from collections import OrderedDict
import itertools

from django.core.exceptions import ImproperlyConfigured
from django.db import models, connection


class ScoreMock(object):
    is_mock = True

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


class ResultSection(object):

    def __init__(self, label, round=None, headers=None):
        self.label = label
        self.round = round
        self.headers = headers

    def __unicode__(self):
        return self.label


class BaseResultMode(object):
    slug = ''
    name = ''
    include_distance_breakdown = False
    ignore_subrounds = False
    subrounds = {}

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __unicode__(self):
        return self.name

    def get_results(self, competition, scores, leaderboard=False, request=None):
        raise ImproperlyConfigured('Subclasses must implement get_results')

    def sort_results(self, scores):
        results = sorted(scores, key=lambda s: (s.score, s.hits, s.golds, s.xs), reverse=True)
        placing = 0
        current_score = None
        placing_counter = 1
        for score in results:
            if score.disqualified or score.guest:
                score.placing = None
            else:
                score_repr = (score.score, score.hits, score.golds, score.xs)
                if score_repr == current_score:
                    placing_counter += 1
                else:
                    current_score = score_repr
                    placing += placing_counter
                    placing_counter = 1
                score.placing = placing
        return results

    def get_section_for_round(self, round):
        headers = ['Pl.'] + self.get_main_headers()
        if self.include_distance_breakdown:
            subrounds = round.subrounds.all()
            if len(subrounds) > 1:
                for subround in round.subrounds.all():
                    headers += ['%s%s' % (subround.distance, subround.unit)]
        headers.append('Score')
        if round.scoring_type == 'X':
            headers += ['10s', 'Xs']
        else:
            headers += ['Hits', 'Golds']
        return ResultSection(
            label=self.label_for_round(round),
            round=round,
            headers=headers,
        )

    def get_main_headers(self):
        return ['Archer', 'Club', None]

    def label_for_round(self, round):
        return unicode(round)

    def get_subrounds(self, score):
        if score.is_team or self.ignore_subrounds:
            return []
        shot_round = score.target.session_entry.session_round.shot_round
        if shot_round not in self.subrounds:
            self.subrounds[shot_round] = shot_round.subrounds.all()
        return self.subrounds[shot_round]

    def score_details(self, score, section):
        from entries.models import SCORING_TOTALS, SCORING_DOZENS, SCORING_FULL
        scores = []
        subrounds = self.get_subrounds(score)
        if self.include_distance_breakdown and len(subrounds) > 1 and not score.target.session_entry.session_round.session.scoring_system == SCORING_TOTALS:
            if score.disqualified or score.target.session_entry.session_round.session.scoring_system == SCORING_TOTALS or hasattr(score, 'is_mock'):
                scores += [''] * len(subrounds)
            else:
                subround_scores = []

                if score.target.session_entry.session_round.session.scoring_system == SCORING_FULL:
                    # Arrow of round has been stored off by a dozen
                    counter = 13
                    for subround in subrounds:
                        subround_scores.append(score.arrow_set.filter(arrow_of_round__in=range(counter, counter + subround.arrows)).aggregate(models.Sum('arrow_value'))['arrow_value__sum'])
                        counter += subround.arrows

                elif score.target.session_entry.session_round.session.scoring_system == SCORING_DOZENS:
                    counter = 1
                    for subround in subrounds:
                        subround_scores.append(score.dozen_set.filter(dozen__in=range(counter, counter + subround.arrows / 12)).aggregate(models.Sum('total'))['total__sum'])
                        counter += subround.arrows / 12

                scores += subround_scores
        if score.disqualified:
            scores += ['DSQ', '', '']
        elif score.retired:
            scores += [score.score, 'Retired', '']
        elif hasattr(score, 'partial_score'):
            scores += [
                score.partial_score,
                score.final_score,
            ]
        elif section.round is None:
            # weekend mode -- TODO: This is also being picked up by the by session results mode
            scores += [
                score.score,
                score.hits,
                score.golds,
                score.xs,
            ]
        elif section.round.scoring_type == 'X':
            scores += [
                score.score,
            ]
            if not self.hide_golds:
                scores += [
                    score.golds,
                    score.xs,
                ]
        else:
            scores += [
                score.score,
            ]
            if not self.hide_golds:
                scores += [
                    score.hits,
                    score.golds,
                ]
        return scores


class BySession(BaseResultMode):
    slug = 'by-session'
    name = 'By session'

    def get_results(self, competition, scores, leaderboard=False, request=None):
        """Get the results for each session, assuming the same round across sessions.

        Strategy:
        - find all sessions
        - go through scores, adding to each category specific sets
            - here respect competition options - novices, juniors, second rounds etc.
        """
        self.leaderboard = leaderboard
        sessions = self.get_sessions(competition)
        return OrderedDict((
            ResultSection(session.start.strftime('%Y/%m/%d %I:%M %p')),
            self.get_session_results(competition, session, scores),
        ) for session in sessions)

    def get_sessions(self, competition):
        return competition.session_set.all()

    def get_session_results(self, competition, session, scores):
        results = OrderedDict()
        for score in scores:
            session_entry = score.target.session_entry
            if session_entry.session_round.session_id is not session.id:
                continue
            if competition.exclude_later_shoots and session_entry.index > 1:
                continue
            category = session_entry.competition_entry.category()
            if category not in results:
                results[category] = []
            results[category].append(score)
        for category in results:
            results[category] = self.sort_results(results[category])
            for i, score in enumerate(results[category]):
                if not self.leaderboard and score.score == 0:
                    results[category][i] = ScoreMock(
                        target=score.target,
                        score='DNS',
                        hits='',
                        golds='',
                        xs='',
                        disqualified=False,
                        retired=False,
                        placing=None,
                    )
        return results


class ByRound(BaseResultMode):
    slug = 'by-round'
    name = 'By round'

    def get_results(self, competition, scores, leaderboard=False, request=None):
        """Get the results for each category, by round.

        Strategy:
        - find all the rounds shot
        - order by the first session they're shot in
        - go through scores, adding to each category specific sets
            - here respect competition options - novices, juniors, second rounds etc.
        """
        self.leaderboard = leaderboard
        rounds = self.get_rounds(competition)
        return OrderedDict((
            self.get_section_for_round(round),
            self.get_round_results(competition, round, scores)
        ) for round in rounds)

    def get_rounds(self, competition):
        from entries.models import SessionRound

        session_rounds = SessionRound.objects.filter(session__competition=competition, olympicsessionround__isnull=True).order_by('session__start').select_related('shot_round')
        rounds = []
        for round in session_rounds:
            if round.shot_round not in rounds:
                rounds.append(round.shot_round)
        return rounds

    def get_round_results(self, competition, round, scores):
        results = OrderedDict()
        for score in scores:
            session_entry = score.target.session_entry
            if session_entry.session_round.shot_round.id is not round.id:
                continue
            if competition.exclude_later_shoots and session_entry.index > 1:
                continue
            category = self.get_category_for_entry(session_entry.competition_entry)
            if category not in results:
                results[category] = []
            results[category].append(score)
        for category in results:
            results[category] = self.sort_results(results[category])
            for i, score in enumerate(results[category]):
                if not self.leaderboard and score.score == 0:
                    results[category][i] = ScoreMock(
                        target=score.target,
                        score='DNS',
                        hits='',
                        golds='',
                        xs='',
                        disqualified=False,
                        retired=False,
                        placing=None,
                    )
        return results

    def get_category_for_entry(self, entry):
        return entry.category()


class ByRoundProgressional(ByRound, BaseResultMode):
    slug = 'by-round-progressional'
    name = 'By round (progressional)'

    def get_results(self, competition, scores, leaderboard=False, request=None):
        if request and request.GET.get('up_to') and scores:
            arrow_of_round = (int(request.GET['up_to']) + 1) * scores[0].target.session_entry.session_round.session.arrows_entered_per_end
            cursor = connection.cursor()
            cursor.execute('''
            SELECT "scores_arrow"."score_id", SUM("scores_arrow"."arrow_value")
            FROM "scores_arrow" WHERE "scores_arrow"."score_id" IN (
                SELECT "scores_score"."id"
                FROM "scores_score"
                INNER JOIN "entries_targetallocation" ON ( "scores_score"."target_id" = "entries_targetallocation"."id" )
                INNER JOIN "entries_sessionentry" ON ( "entries_targetallocation"."session_entry_id" = "entries_sessionentry"."id" )
                INNER JOIN "entries_competitionentry" ON ( "entries_sessionentry"."competition_entry_id" = "entries_competitionentry"."id" )
                WHERE "entries_competitionentry"."competition_id" = %s
            ) AND "scores_arrow"."arrow_of_round" <= %s GROUP BY "scores_arrow"."score_id";
            ''', (
                competition.pk,
                arrow_of_round,
            ))
            rows = cursor.fetchall()
            partial_scores = dict(rows)
            cursor.close()
            for score in scores:
                partial = partial_scores.get(score.pk)
                if partial is not None:
                    if not score.score == partial:
                        score.final_score = '(%s)' % score.score
                    else:
                        score.final_score = ''
                    score.partial_score = partial
        self.leaderboard = leaderboard
        rounds = self.get_rounds(competition)
        return OrderedDict((
            self.get_section_for_round(round),
            self.get_round_results(competition, round, scores)
        ) for round in rounds)


class DoubleRound(BaseResultMode):
    slug = 'double-round'
    name = 'Double round'

    def get_results(self, competition, scores, leaderboard=False, request=None):
        """Get the results for each category, by round.

        Strategy:
        - find all the rounds shot
        - order by the first session they're shot in
        - go through scores, adding to each category specific sets
        - need to add a quacking score object which is the double
        """
        self.leaderboard = leaderboard
        rounds = self.get_rounds(competition)
        return OrderedDict((
            self.get_section_for_round(round),
            self.get_round_results(competition, round, scores)
        ) for round in rounds)

    def get_rounds(self, competition):
        from entries.models import SessionRound

        session_rounds = SessionRound.objects.filter(session__competition=competition).order_by('session__start')
        rounds = []
        for round in session_rounds:
            if round.shot_round not in rounds:
                rounds.append(round.shot_round)
        return rounds

    def get_round_results(self, competition, round, scores):
        results = OrderedDict()
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

    def label_for_round(self, round):
        return 'Double %s' % unicode(round)


class H2HSeedings(ByRound, BaseResultMode):
    slug = 'seedings'
    name = 'Seedings'

    def get_rounds(self, competition):
        from entries.models import SessionRound
        from olympic.models import Category

        self.categories = Category.objects.filter(olympicsessionround__session__competition=competition).prefetch_related('bowstyles')

        session_rounds = SessionRound.objects.filter(session__competition=competition, olympicsessionround__isnull=False).order_by('session__start')
        rounds = []
        for round in session_rounds:
            if round.shot_round not in rounds:
                rounds.append(round.shot_round)
        return rounds

    def get_results(self, competition, scores, leaderboard=False, request=None):
        self.leaderboard = leaderboard
        rounds = self.get_rounds(competition)
        return OrderedDict((
            self.get_section_for_round(round),
            self.get_round_results(competition, round, scores)
        ) for round in rounds)

    def get_category_for_entry(self, entry):
        for category in self.categories:
            if entry.bowstyle in category.bowstyles.all():
                if category.gender is None or category.gender == entry.archer.gender:
                    return category


class Team(BaseResultMode):
    slug = 'team'
    name = 'Teams'

    def __init__(self, **kwargs):
        super(Team, self).__init__(**kwargs)
        self.include_distance_breakdown = False  # always for teams

    def get_results(self, competition, scores, leaderboard=False, request=None):
        """
        Strategy:
        - split by team
            - find the top scores in each team
            - filter out incomplete teams
            - aggregate and order
        - repeat for each team type
        """
        clubs = {}
        round = None
        for score in scores:
            if not leaderboard and not score.score:
                continue
            session_entry = score.target.session_entry
            if round is None:
                round = session_entry.session_round.shot_round
            club = session_entry.competition_entry.club
            if session_entry.index > 1 and competition.exclude_later_shoots:
                continue
            if score.disqualified or score.retired:
                continue
            if competition.strict_b_teams:
                if session_entry.competition_entry.b_team:
                    club = '%s (B)' % club.short_name
            if competition.strict_c_teams:
                if session_entry.competition_entry.c_team:
                    club = '%s (C)' % club.short_name
            if club not in clubs:
                clubs[club] = []
            clubs[club].append(score)
        if not clubs:
            return {}
        results = OrderedDict()
        for type in self.get_team_types(competition):
            results[type] = self.get_team_scores(competition, clubs, type)
        return {self.get_section_for_round(round): results}

    def get_team_types(self, competition):
        # TODO: support team types properly
        team_types = ['Non-compound']
        if competition.split_gender_teams:
            team_types = ['Gents non-compound', 'Ladies non-compound']
        if competition.compound_team_size is not None:
            team_types.append('Compound')
        if competition.junior_team_size is not None:
            team_types.append('Junior')
        if competition.has_novices:
            team_types.append('Novice')
        return team_types

    def get_team_scores(self, competition, clubs, type):
        club_results = []
        sessions = competition.session_set.filter(sessionround__isnull=False).distinct()
        for club, club_scores in clubs.items():
            club_scores = [s for s in club_scores if self.is_valid_for_type(s, type, competition)]
            if competition.combine_rounds_for_team_scores:
                club_scores = self.combine_rounds(club_scores)
            club_scores = sorted(club_scores, key=lambda s: (s.score, s.hits, s.golds, s.xs), reverse=True)
            team_size = competition.team_size
            if type == 'Novice' and competition.novice_team_size:
                team_size = competition.novice_team_size
            if type == 'Compound' and competition.compound_team_size:
                team_size = competition.compound_team_size
            if type == 'Junior' and competition.junior_team_size:
                team_size = competition.junior_team_size
            if competition.force_mixed_teams:
                gent_found = False
                lady_found = False
                mixed_team_found = False
                for i, score in enumerate(club_scores):
                    if score.target.session_entry.competition_entry.archer.gender == 'G':
                        gent_found = True
                    else:
                        lady_found = True
                    if gent_found and lady_found:
                        if i >= team_size:
                            club_scores = club_scores[:team_size - 1] + [score]
                        else:
                            club_scores = club_scores[:team_size]
                        mixed_team_found = True
                        break
                if not mixed_team_found:
                    club_scores = []
            else:
                club_scores = club_scores[:team_size]
            if not club_scores:
                continue
            if len(club_scores) < team_size and not competition.allow_incomplete_teams:
                continue
            if getattr(club_scores[0], 'components', None):
                club_scores = sum((s.components for s in club_scores), [])
            if competition.combine_rounds_for_team_scores and not competition.allow_incomplete_teams and len(club_scores) < (team_size * len(sessions)):
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

    def is_valid_for_type(self, score, type, competition):
        if score.target.session_entry.competition_entry.guest:
            return False
        is_non_compound = not score.target.session_entry.competition_entry.bowstyle.name == 'Compound'
        if type == 'Non-compound':
            if not competition.novices_in_experienced_teams:
                return is_non_compound and score.target.session_entry.competition_entry.novice == 'E'
            return is_non_compound
        if type == 'Gents non-compound':
            if not competition.novices_in_experienced_teams:
                return (is_non_compound
                        and score.target.session_entry.competition_entry.novice == 'E'
                        and score.target.session_entry.competition_entry.archer.gender == 'G')
            return is_non_compound and score.target.session_entry.competition_entry.archer.gender == 'G'
        if type == 'Ladies non-compound':
            if not competition.novices_in_experienced_teams:
                return (is_non_compound
                        and score.target.session_entry.competition_entry.novice == 'E'
                        and score.target.session_entry.competition_entry.archer.gender == 'L')
            return is_non_compound and score.target.session_entry.competition_entry.archer.gender == 'L'
        if type == 'Compound':
            return not is_non_compound
        if type == 'Novice':
            return is_non_compound and score.target.session_entry.competition_entry.novice == 'N'
        if type == 'Junior':
            is_junior = score.target.session_entry.competition_entry.age == 'J'
            if not competition.novices_in_experienced_teams:
                return is_junior and is_non_compound and score.target.session_entry.competition_entry.novice == 'E'
            return is_junior and is_non_compound

    def get_main_headers(self):
        return ['Club']

    def label_for_round(self, round):
        return 'Team'

    def combine_rounds(self, club_scores):
        ce_getter = lambda s: s.target.session_entry.competition_entry
        combined_scores = []
        for competition_entry, scores in itertools.groupby(club_scores, ce_getter):
            scores = list(scores)
            combined_scores.append(ScoreMock(
                score=sum(s.score for s in scores),
                hits=sum(s.hits for s in scores),
                golds=sum(s.golds for s in scores),
                xs=sum(s.xs for s in scores),
                target=scores[0].target,
                components=scores,
            ))
        return combined_scores


class Weekend(BaseResultMode):
    slug = 'weekend'
    name = 'Weekend (Masters style)'
    ignore_subrounds = True

    def __init__(self, **kwargs):
        self.init_kwargs = kwargs

    def get_results(self, competition, scores, leaderboard=False, request=None):
        """
        Strategy:
         - Get the results for the two rounds as if they were normal shoots
         - Exclude dead categories?
         - Get the results from the H2H
         - Work out points
         - Order, resolve ties
         - Format!
        """
        from olympic.models import OlympicSessionRound

        all_fita_results = ByRound(**self.init_kwargs).get_results(competition, scores, leaderboard=leaderboard, request=request)
        seeding_results = H2HSeedings(**self.init_kwargs).get_results(competition, scores, leaderboard=leaderboard, request=request)
        h2h_categories = OlympicSessionRound.objects.filter(session__competition=competition).select_related('category')

        full_results = OrderedDict()

        class TargetMock(object):
            def __init__(self, seed):
                seed.competition_entry = seed.entry
                self.session_entry = seed

        for category in h2h_categories:
            h2h_results = category.get_results()
            results = []
            for round in all_fita_results:
                if category.category.gender == 'G' and round.round.name == 'WA 1440 (Gents)':
                    fita = round
                    break
                if category.category.gender == 'L' and round.round.name == 'WA 1440 (Ladies)':
                    fita = round
                    break
            for division in all_fita_results[fita]:
                if 'Compound' in unicode(category.category) and 'Compound' in division:
                    if category.category.gender == 'G' and 'Gent' in division:
                        fita_results = all_fita_results[fita][division]
                        break
                    if category.category.gender == 'L' and 'Lady' in division:
                        fita_results = all_fita_results[fita][division]
                        break
                if 'Recurve' in unicode(category.category) and 'Recurve' in division:
                    if category.category.gender == 'G' and 'Gent' in division:
                        fita_results = all_fita_results[fita][division]
                        break
                    if category.category.gender == 'L' and 'Lady' in division:
                        fita_results = all_fita_results[fita][division]
                        break

            fita_results_by_entry = {
                result.target.session_entry.competition_entry: result for result in fita_results
            }

            for round, divisions in seeding_results.items():
                for division in divisions:
                    if 'Compound' in unicode(category.category) and '50m' in round.round.name:
                        if category.category.gender == 'G' and division.gender == 'G':
                            ranking_results = seeding_results[round][division]
                            break
                        if category.category.gender == 'L' and division.gender == 'L':
                            ranking_results = seeding_results[round][division]
                            break
                    if 'Recurve' in unicode(category.category) and '70m' in round.round.name:
                        if category.category.gender == 'G' and division.gender == 'G':
                            ranking_results = seeding_results[round][division]
                            break
                        if category.category.gender == 'L' and division.gender == 'L':
                            ranking_results = seeding_results[round][division]
                            break

            ranking_results_by_entry = {
                result.target.session_entry.competition_entry: result for result in ranking_results
            }

            weekend_results = []
            for seed in h2h_results.results:
                entry = seed.entry
                if entry not in fita_results_by_entry:
                    continue
                fita_result = fita_results_by_entry[entry]
                if fita_result.retired or fita_result.score == 0 or fita_result.placing is None:
                    continue
                ranking_result = ranking_results_by_entry[entry]
                if ranking_result.retired or ranking_result.score == 0 or ranking_result.placing is None:
                    continue
                weekend_results.append(ScoreMock(
                    target=TargetMock(seed),
                    score=ranking_result.placing,
                    hits=seed.rank,
                    golds=fita_result.placing,
                    xs=ranking_result.placing + seed.rank + fita_result.placing,
                    disqualified=False,
                    retired=False,
                    placing=seed.rank,
                ))

            results = sorted(weekend_results, key=lambda s: (s.xs, s.hits, s.golds))
            for i, result in enumerate(results, 1):
                result.placing = i
            full_results[category.category.short_name] = results

        headers = ['Pl.'] + self.get_main_headers() + ['720', 'H2H', '1440', 'Total']
        section = ResultSection('Weekend results', None, headers)
        return {section: full_results}


def get_result_modes():
    modes = BaseResultMode.__subclasses__()
    return [(mode.slug, mode.name) for mode in modes]


def get_mode(slug, **kwargs):
    modes = BaseResultMode.__subclasses__()
    try:
        return [mode(**kwargs) for mode in modes if mode.slug == slug][0]
    except IndexError:
        return None

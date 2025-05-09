import itertools
from collections import OrderedDict

from django.core.exceptions import ImproperlyConfigured
from django.db import connection, models


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

    def __str__(self):
        return self.label


class ResultCategory(object):
    def __init__(self, bowstyle, gender, junior=None, novice=None):
        self.bowstyle = bowstyle
        self.gender = gender
        self.junior = junior
        self.novice = novice

    def __str__(self):
        parts = filter(None, [
            self.novice,
            str(self.bowstyle),
            self.junior,
            self.gender,
        ])
        return ' '.join(parts)

    def __eq__(self, other):
        return (
            self.bowstyle,
            self.gender,
            self.junior,
            self.novice,
        ) == (
            other.bowstyle,
            other.gender,
            other.junior,
            other.novice,
        )

    def __hash__(self):
        return hash((
            self.bowstyle.pk,
            self.gender,
            self.junior,
            self.novice,
        ))


class BaseResultMode(object):
    slug = ''
    name = ''
    include_distance_breakdown = False
    ignore_subrounds = False
    subrounds = {}

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return self.name

    def get_results(self, competition, scores, leaderboard=False, request=None):
        raise ImproperlyConfigured('Subclasses must implement get_results')

    def sort_results(self, scores):
        scores = sorted(scores, key=lambda s: (-int(s.retired), s.score, s.hits, s.golds, s.xs, s.tiebreak), reverse=True)
        placing = 0
        current_score = None
        placing_counter = 1
        results = []
        for score in scores:
            if not isinstance(score, ScoreMock):
                score = ScoreMock(
                    pk=score.pk,
                    target=score.target,
                    score=score.score,
                    hits=score.hits,
                    golds=score.golds,
                    xs=score.xs,
                    tiebreak=score.tiebreak,
                    disqualified=score.disqualified,
                    is_actual_zero=score.is_actual_zero,
                    retired=score.retired,
                    source=score,
                )
            if score.disqualified or score.guest or score.retired:
                score.placing = None
            else:
                score_repr = (score.score, score.hits, score.golds, score.xs, score.tiebreak)
                if score_repr == current_score:
                    placing_counter += 1
                else:
                    current_score = score_repr
                    placing += placing_counter
                    placing_counter = 1
                score.placing = placing
            results.append(score)
        return results

    def get_section_for_round(self, round, competition, is_team=False):
        headers = ['Pl.'] + self.get_main_headers(competition)
        if competition.has_juniors or not competition.split_categories_on_agb_age and not is_team:
            headers += ['Age']
        if competition.has_novices and not is_team:
            headers += ['']
        if self.include_distance_breakdown and hasattr(round, 'subrounds'):
            subrounds = round.subrounds.all()
            if len(subrounds) > 1:
                for subround in round.subrounds.all():
                    headers += ['%s%s' % (subround.distance, subround.unit)]
            elif round.can_split:
                subround = subrounds[0]
                headers += [
                    '%s%s-1' % (subround.distance, subround.unit),
                    '%s%s-2' % (subround.distance, subround.unit),
                ]
        headers.append('Score')
        if round.scoring_type == 'X':
            headers += ['10s', 'Xs']
        elif round.scoring_type == 'E':
            headers += ['11s', '10s']
        elif round.scoring_type == 'I':
            headers += ['10s']
        elif round.scoring_type == 'S':
            pass
        else:
            headers += ['Hits', 'Golds']
        return ResultSection(
            label=self.label_for_round(round),
            round=round,
            headers=headers,
        )

    def get_main_headers(self, competition):
        if competition.use_county_teams:
            return ['Archer', 'County']
        if competition.ifaa_rules:
            return ['Archer', 'Country']
        return ['Archer', 'Club']

    def label_for_round(self, round):
        return str(round)

    def get_subrounds(self, score):
        if score.is_team or self.ignore_subrounds:
            return []
        shot_round = score.target.session_entry.session_round.shot_round
        if shot_round not in self.subrounds:
            self.subrounds[shot_round] = shot_round.subrounds.all()
        return self.subrounds[shot_round]

    def score_details(self, score, section):
        from entries.models import (
            SCORING_ARCHER, SCORING_DOZENS, SCORING_FULL, SCORING_TOTALS,
        )
        scores = []
        if self.include_distance_breakdown:
            shot_round = score.target.session_entry.session_round.shot_round
            subrounds = self.get_subrounds(score)
            if len(subrounds) > 1 and not score.target.session_entry.session_round.session.scoring_system == SCORING_TOTALS:
                if score.disqualified or score.target.session_entry.session_round.session.scoring_system == SCORING_TOTALS:
                    scores += [''] * len(subrounds)
                elif not hasattr(score, 'source'):
                    scores += [''] * len(subrounds)
                else:
                    score = score.source
                    subround_scores = []

                    if score.target.session_entry.session_round.session.scoring_system in [SCORING_FULL, SCORING_ARCHER]:
                        counter = 1
                        for subround in subrounds:
                            subround_scores.append(score.arrow_set.filter(arrow_of_round__in=range(counter, counter + subround.arrows)).aggregate(models.Sum('arrow_value'))['arrow_value__sum'] or 0)
                            counter += subround.arrows

                    elif score.target.session_entry.session_round.session.scoring_system == SCORING_DOZENS:
                        counter = 1
                        for subround in subrounds:
                            subround_scores.append(score.dozen_set.filter(dozen__in=range(counter, counter + int(subround.arrows / 12))).aggregate(models.Sum('total'))['total__sum'])
                            counter += int(subround.arrows / 12)

                    scores += subround_scores
            elif shot_round.can_split:
                if score.disqualified or score.target.session_entry.session_round.session.scoring_system == SCORING_TOTALS or not hasattr(score, 'source'):
                    scores += ['', '']
                else:
                    score = score.source
                    arrows = score.arrow_set.order_by('arrow_of_round').values_list('arrow_value', flat=True)
                    scores += [
                        sum(arrows[:(shot_round.arrows / 2)], 0),
                        sum(arrows[(shot_round.arrows / 2):]),
                    ]
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
            # weekend mode -- TODO: Make sure this has better round type data, also look at by session if not all rounds are identical...
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
        elif section.round.scoring_type == 'E':
            scores += [
                score.score,
            ]
            if not self.hide_golds:
                scores += [
                    score.xs,
                    score.golds,
                ]
        elif section.round.scoring_type == 'I':
            scores += [
                score.score,
            ]
            if not self.hide_golds:
                scores += [
                    score.golds,
                ]
        elif section.round.scoring_type == 'S':
            scores += [score.score]
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

    def get_categories_for_entry(self, competition, entry):
        kwargs = {
            'gender': entry.get_gender_display(),
            'bowstyle': entry.bowstyle,
        }
        if competition.has_juniors and entry.age == 'J':
            kwargs['junior'] = 'Junior'
        if competition.has_agb_age_groups and competition.split_categories_on_agb_age and entry.agb_age:
            kwargs['junior'] = entry.get_agb_age_display()
        if competition.ifaa_rules and entry.ifaa_division:
            kwargs['junior'] = entry.get_ifaa_division_display()
        if competition.has_novices and entry.novice == 'N':
            kwargs['novice'] = 'Novice'
        categories = [ResultCategory(**kwargs)]
        if competition.novices_in_experienced_individual and entry.novice == 'N':
            kwargs.pop('novice')
            categories.append(ResultCategory(**kwargs))
        return categories


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
        headers = ['Pl.'] + self.get_main_headers(competition)
        round = scores[0].target.session_entry.session_round.shot_round
        headers.append('Score')
        if round.scoring_type == 'X':
            headers += ['10s', 'Xs']
        elif round.scoring_type == 'E':
            headers += ['11s', '10s']
        elif round.scoring_type == 'I':
            headers += ['10s']
        elif round.scoring_type == 'S':
            pass
        else:
            headers += ['Hits', 'Golds']
        return OrderedDict((
            ResultSection(
                session.start.strftime('%Y/%m/%d %I:%M %p'),
                round=round,
                headers=headers,
            ),
            self.get_session_results(competition, session, scores),
        ) for session in sessions)

    def get_sessions(self, competition):
        return competition.session_set.all()

    def get_session_results(self, competition, session, scores):
        results = OrderedDict()
        for score in scores:
            session_entry = score.target.session_entry
            if session_entry.session_round.session_id != session.id:
                continue
            categories = self.get_categories_for_entry(competition, session_entry.competition_entry)
            for category in categories:
                if category not in results:
                    results[category] = []
                results[category].append(score)
        for category in results:
            results[category] = self.sort_results(results[category])
            for i, score in enumerate(results[category]):
                if not self.leaderboard and score.score == 0 and not getattr(score, 'is_actual_zero', False):
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
    include_later_shoots_anyway = False

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
            self.get_section_for_round(round, competition),
            self.get_round_results(competition, [round], scores)
        ) for round in rounds)

    def get_rounds(self, competition):
        from entries.models import Competition, SessionRound

        if isinstance(competition, Competition):
            session_rounds = SessionRound.objects.filter(
                session__competition=competition,
            ).exclude(olympicsessionround__exclude_ranking_rounds=True).order_by(
                'session__start',
                '-shot_round__longest_distance',
            ).select_related('shot_round')
        else:
            # We have a league leg
            session_rounds = SessionRound.objects.filter(
                session__competition__in=competition.competitions.all(),
            ).exclude(olympicsessionround__exclude_ranking_rounds=True).order_by('session__start').select_related('shot_round')
        rounds = []
        for round in session_rounds:
            if round.shot_round not in rounds:
                rounds.append(round.shot_round)
        return rounds

    def get_round_results(self, competition, rounds, scores, category=None):
        results = OrderedDict()
        for score in scores:
            session_entry = score.target.session_entry
            if session_entry.session_round.shot_round.id not in [round.id for round in rounds]:
                continue
            if not self.include_later_shoots_anyway and competition.exclude_later_shoots and session_entry.index > 1:
                continue
            if category:  # passed in from Seedings
                categories = [category]
            else:
                categories = self.get_categories_for_entry(competition, session_entry.competition_entry)
            for cat in categories:
                if cat not in results:
                    results[cat] = []
                results[cat].append(score)
        for cat in results:
            results[cat] = self.sort_results(results[cat])
            for i, score in enumerate(results[cat]):
                if not self.leaderboard and score.score == 0 and not getattr(score, 'is_actual_zero', False):
                    results[cat][i] = ScoreMock(
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


class ByRoundAllShot(ByRound, BaseResultMode):
    slug = 'all-shot'
    name = 'By round (include later shoots)'
    include_later_shoots_anyway = True


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
                    score.score = partial
        self.leaderboard = leaderboard
        rounds = self.get_rounds(competition)
        return OrderedDict((
            self.get_section_for_round(round, competition),
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
        rounds, valid_session_rounds = self.get_rounds(competition)
        return OrderedDict((
            self.get_section_for_round(round, competition),
            self.get_round_results(competition, round, valid_session_rounds, scores)
        ) for round in rounds)

    def get_rounds(self, competition):
        from entries.models import SessionRound

        session_rounds = SessionRound.objects.filter(session__competition=competition).order_by('session__start').exclude(
            olympicsessionround__exclude_ranking_rounds=True,
        )
        rounds = []
        valid_session_rounds = []
        for round in session_rounds:
            if round.shot_round not in rounds:
                rounds.append(round.shot_round)
            valid_session_rounds.append(round)
        return rounds, valid_session_rounds

    def get_round_results(self, competition, round, valid_session_rounds, scores):
        results = OrderedDict()
        for score in scores:
            session_entry = score.target.session_entry
            if session_entry.session_round.shot_round.id != round.id:
                continue
            if session_entry.session_round not in valid_session_rounds:
                continue
            categories = self.get_categories_for_entry(competition, session_entry.competition_entry)
            for category in categories:
                if category not in results:
                    results[category] = {}
                if session_entry.competition_entry not in results[category]:
                    results[category][session_entry.competition_entry] = []
                results[category][session_entry.competition_entry].append(score)
        categories_to_remove = []
        for category, scores in results.items():
            scores = OrderedDict((entry, rounds) for entry, rounds in scores.items() if len(rounds) >= 2)
            if not scores:
                categories_to_remove.append(category)
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
                tiebreak=None,
            ) for entry, sub_scores in scores.items()]
            if not self.leaderboard:
                new_scores = filter(lambda s: s.score > 0, new_scores)
            results[category] = self.sort_results(new_scores)
        for category in categories_to_remove:
            results.pop(category)
        return results

    def label_for_round(self, round):
        return 'Double %s' % str(round)


class CombinedRounds(BaseResultMode):
    slug = 'combined-rounds'
    name = 'Combined rounds'

    def get_results(self, competition, scores, leaderboard=False, request=None):
        """Get the results for each category, by combined all scores.

        Strategy:
        - find the first round shot for result formatting
        - go through scores, adding to each category specific sets
        - need to add a quacking score object which is the combination of all the scores
        """
        from entries.models import SessionRound

        self.leaderboard = leaderboard
        self.include_distance_breakdown = True

        shot_round = SessionRound.objects.filter(session__competition=competition).order_by('session__start').exclude(
            olympicsessionround__exclude_ranking_rounds=True,
        ).first().shot_round
        headers = ['Pl.'] + self.get_main_headers(competition)
        section = ResultSection('Combined scores', shot_round, headers)
        return {
            section: self.get_round_results(competition, scores)
        }

    def get_round_results(self, competition, scores):
        results = OrderedDict()
        for score in scores:
            session_entry = score.target.session_entry
            categories = self.get_categories_for_entry(competition, session_entry.competition_entry)
            for category in categories:
                if category not in results:
                    results[category] = {}
                if session_entry.competition_entry not in results[category]:
                    results[category][session_entry.competition_entry] = []
                results[category][session_entry.competition_entry].append(score)
        for category, scores in results.items():
            if not scores:
                results.pop(category)
                continue
            for entry in scores:
                scores[entry] = sorted(scores[entry], key=lambda s: s.target.session_entry.session_round.session.start)
            new_scores = [ScoreMock(
                disqualified=any(s.disqualified for s in sub_scores),
                retired=any(s.disqualified for s in sub_scores),
                target=sub_scores[0].target,
                score=sum(s.score for s in sub_scores),
                subrounds=[s.score for s in sub_scores],
                hits=sum(s.hits for s in sub_scores),
                golds=sum(s.golds for s in sub_scores),
                xs=sum(s.xs for s in sub_scores),
                tiebreak=sum(s.tiebreak for s in sub_scores),
            ) for entry, sub_scores in scores.items()]
            if not self.leaderboard:
                new_scores = filter(lambda s: s.score > 0, new_scores)
            results[category] = self.sort_results(new_scores)
        return results

    def get_subrounds(self, score):
        return score.subrounds

    def label_for_round(self, round):
        return 'Combined scores'


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
        clubs, round = self.split_by_club(scores, competition, leaderboard)
        if not clubs:
            return {}
        results = OrderedDict()
        for type in self.get_team_types(competition):
            type_results = self.get_team_scores(competition, clubs, type)
            if type_results:
                results[type] = type_results
        return {self.get_section_for_round(round, competition, is_team=True): results}

    def split_by_club(self, scores, competition, leaderboard, valid_rounds=None):
        from entries.models import Competition, SessionRound

        if isinstance(competition, Competition) and not valid_rounds:
            session_rounds = SessionRound.objects.filter(
                session__competition=competition,
            ).exclude(
                olympicsessionround__exclude_ranking_rounds=True,
            ).order_by('session__start').select_related('shot_round')
        elif not valid_rounds:
            # We have a league leg
            session_rounds = SessionRound.objects.filter(
                session__competition__in=competition.competitions.all(),
            ).exclude(
                olympicsessionround__exclude_ranking_rounds=True,
            ).order_by('session__start').select_related('shot_round')
        else:
            session_rounds = valid_rounds
        round = None
        clubs = {}
        for score in scores:
            if not leaderboard and not score.score:
                continue
            session_entry = score.target.session_entry
            if session_entry.session_round not in session_rounds:
                continue
            if round is None:
                round = session_entry.session_round.shot_round
            club = session_entry.competition_entry.team_name()
            if not club:
                continue
            if session_entry.index > 1 and competition.exclude_later_shoots:
                continue
            if score.disqualified or score.retired:
                continue
            if club not in clubs:
                clubs[club] = []
            clubs[club].append(score)
        return clubs, round

    def get_team_types(self, competition):
        # TODO: support team types properly
        if competition.use_county_teams:
            return [
                'Recurve',
                'Compound',
                'Barebow',
                'Longbow',
                'Junior Recurve',
                'Junior Compound',
            ]
        team_types = []
        if competition.team_size:
            if competition.split_gender_teams:
                team_types += ['Non-compound Men', 'Non-compound Women']
            else:
                team_types.append('Non-compound')
        if competition.any_bow_team_size is not None:
            team_types.append('All bows')
        if competition.recurve_team_size is not None:
            team_types.append('Recurve')
        if competition.barebow_team_size is not None:
            team_types.append('Barebow')
        if competition.compound_team_size is not None:
            team_types.append('Compound')
        if competition.junior_team_size is not None:
            team_types.append('Junior')
        if competition.novice_team_size is not None:
            team_types.append('Novice')
        return team_types

    def get_team_scores(self, competition, clubs, type):
        club_results = []
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
            if type in ['Longbow', 'Barebow'] and competition.use_county_teams:
                # bit of a hack to treat compound team size as "minor team size"
                team_size = competition.compound_team_size
            if type == 'All bows' and competition.any_bow_team_size:
                team_size = competition.any_bow_team_size
            if type == 'Recurve' and competition.recurve_team_size:
                team_size = competition.recurve_team_size
            if type == 'Barebow' and competition.barebow_team_size:
                team_size = competition.barebow_team_size
            if type == 'Junior' and competition.junior_team_size:
                team_size = competition.junior_team_size
            if competition.force_mixed_teams or (competition.force_mixed_teams_recurve_only and type == 'Recurve'):
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
            if competition.combine_rounds_for_team_scores and not competition.allow_incomplete_teams:
                sessions = competition.session_set.filter(sessionround__isnull=False).distinct()
                if len(club_scores) < (team_size * len(sessions)):
                    continue
            team = ScoreMock(
                score=sum(s.score for s in club_scores),
                hits=sum(s.hits for s in club_scores),
                golds=sum(s.golds for s in club_scores),
                xs=sum(s.xs for s in club_scores),
                tiebreak=0,
                club=club,
                team=club_scores,
            )
            club_results.append((club, team))
        return self.sort_results([c[1] for c in club_results])

    def is_valid_for_type(self, score, type, competition):
        if score.target.session_entry.competition_entry.guest:
            return False
        if competition.use_county_teams:
            bowstyle = score.target.session_entry.competition_entry.bowstyle.name
            is_junior = score.target.session_entry.competition_entry.age == 'J'
            if type in ['Recurve', 'Compound', 'Barebow', 'Longbow']:
                return not is_junior and bowstyle == type
            if type in ['Junior Recurve', 'Junior Compound']:
                return is_junior and 'Junior %s' % bowstyle == type
        is_non_compound = not score.target.session_entry.competition_entry.bowstyle.name == 'Compound'
        if type == 'All bows':
            return True
        if type == 'Non-compound':
            if not competition.novices_in_experienced_teams:
                return is_non_compound and score.target.session_entry.competition_entry.novice == 'E'
            return is_non_compound
        if type == 'Non-compound Men':
            if not competition.novices_in_experienced_teams:
                return (is_non_compound and
                        score.target.session_entry.competition_entry.novice == 'E' and
                        score.target.session_entry.competition_entry.archer.gender == 'G')
            return is_non_compound and score.target.session_entry.competition_entry.archer.gender == 'G'
        if type == 'Non-compound Women':
            if not competition.novices_in_experienced_teams:
                return (is_non_compound and
                        score.target.session_entry.competition_entry.novice == 'E' and
                        score.target.session_entry.competition_entry.archer.gender == 'L')
            return is_non_compound and score.target.session_entry.competition_entry.archer.gender == 'L'
        if type in ['Recurve', 'Compound', 'Barebow', 'Longbow']:
            bowstyle = score.target.session_entry.competition_entry.bowstyle.name
            return bowstyle == type
        if type == 'Novice':
            return is_non_compound and score.target.session_entry.competition_entry.novice == 'N'
        if type == 'Junior':
            is_junior = score.target.session_entry.competition_entry.age == 'J'
            if not competition.novices_in_experienced_teams:
                return is_junior and is_non_compound and score.target.session_entry.competition_entry.novice == 'E'
            return is_junior and is_non_compound

    def get_main_headers(self, competition):
        return ['County' if competition.use_county_teams else 'Club']

    def label_for_round(self, round):
        return 'Team'

    def combine_rounds(self, club_scores):
        combined_scores = []
        for competition_entry, scores in itertools.groupby(club_scores,
                lambda s: s.target.session_entry.competition_entry):
            scores = list(scores)
            combined_scores.append(ScoreMock(
                score=sum(s.score for s in scores),
                hits=sum(s.hits for s in scores),
                golds=sum(s.golds for s in scores),
                xs=sum(s.xs for s in scores),
                tiebreak=sum(s.tiebreak for s in scores),
                target=scores[0].target,
                components=scores,
            ))
        return combined_scores


class H2HSeedings(ByRound, Team, BaseResultMode):
    slug = 'seedings'
    name = 'Seedings'

    def get_rounds(self, competition):
        from olympic.models import OlympicSessionRound

        session_rounds = OlympicSessionRound.objects.filter(session__competition=competition).select_related('category').prefetch_related('ranking_rounds', 'category__bowstyles').order_by('id')
        self.categories = [session_round.category for session_round in session_rounds]
        return session_rounds

    def get_results(self, competition, scores, leaderboard=False, request=None):
        self.leaderboard = leaderboard
        rounds = self.get_rounds(competition)
        results = OrderedDict()
        for round in rounds:
            section = self.get_section_for_round(round, competition)
            section.seedings_confirmed = round.seeding_set.exists()
            section_scores = self.filter_scores(competition, scores, round)
            section_results = self.get_round_results(competition, round, section_scores, section.seedings_confirmed, leaderboard)
            results[section] = section_results
        return results

    def get_round_results(self, competition, round, scores, seedings_confirmed, leaderboard):
        if not round.shot_round.team_type:
            if seedings_confirmed:
                results = []
                score_lookup = {score.target.session_entry.competition_entry: score for score in scores}
                for seeding in round.seeding_set.order_by('seed').select_related('entry'):
                    score = score_lookup.get(seeding.entry)
                    if not score:
                        continue
                    score = ScoreMock(
                        pk=score.pk,
                        target=score.target,
                        score=score.score,
                        hits=score.hits,
                        golds=score.golds,
                        xs=score.xs,
                        tiebreak=score.tiebreak,
                        disqualified=score.disqualified,
                        retired=score.retired,
                        source=score,
                        placing=seeding.seed,
                    )
                    results.append(score)
                return {round.category: results}
            results = ByRound.get_round_results(self, competition, [round.shot_round for round in round.ranking_rounds.all()], scores, category=round.category)
            if round.cut:
                for category, provisional_seedings in results.items():
                    for seed in provisional_seedings:
                        if seed.placing and seed.placing > round.cut:
                            seed.missed_cut = True
            return results
        clubs, _ = self.split_by_club(scores, competition, leaderboard, round.ranking_rounds.all())
        # This is pretty hack because team scores aren't bound to categories
        bowstyles = round.category.bowstyles.values_list('name', flat=True)
        if 'Compound' in bowstyles:
            team_scores = self.get_team_scores(competition, clubs, 'Compound')
        else:
            team_scores = self.get_team_scores(competition, clubs, 'Non-compound')
        if seedings_confirmed:
            team_seedings = []
            team_lookup = {score.club: score for score in team_scores}
            if team_lookup:
                for seeding in round.seeding_set.order_by('seed').select_related('entry'):
                    if seeding.entry.team_name() in team_lookup:
                        team_seedings.append(team_lookup[seeding.entry.team_name()])
            return {round.category: team_seedings}
        return {round.category: team_scores}

    def label_for_round(self, round):
        return str(round.shot_round)

    def get_main_headers(self, competition):
        if competition.use_county_teams:
            return ['Archer', 'County']
        return ['Archer', 'Club']

    def filter_scores(self, competition, scores, round):
        filtered = []
        ranking_rounds = round.ranking_rounds.all()
        for score in scores:
            competition_entry = score.target.session_entry.competition_entry
            categories = self.get_categories_for_entry(competition, competition_entry)
            if round.category in categories and score.target.session_entry.session_round in ranking_rounds:
                filtered.append(score)
        return filtered

    def get_categories_for_entry(self, competition, entry):
        categories = []
        for category in self.categories:
            if entry.bowstyle in category.bowstyles.all():
                if ((category.gender is None or category.gender == entry.archer.gender) and
                        (category.novice is None or category.novice == entry.novice) and
                        (not category.ages or entry.agb_age in category.ages)):
                    categories.append(category)
        return categories


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
                if category.category.gender == 'G' and round.round.name == 'WA 1440 (Men)':
                    fita = round
                    break
                if category.category.gender == 'L' and round.round.name == 'WA 1440 (Women)':
                    fita = round
                    break
            for division in all_fita_results[fita]:
                if 'Compound' in str(category.category) and 'Compound' in division:
                    if category.category.gender == 'G' and 'Men' in division:
                        fita_results = all_fita_results[fita][division]
                        break
                    if category.category.gender == 'L' and 'Women' in division:
                        fita_results = all_fita_results[fita][division]
                        break
                if 'Recurve' in str(category.category) and 'Recurve' in division:
                    if category.category.gender == 'G' and 'Men' in division:
                        fita_results = all_fita_results[fita][division]
                        break
                    if category.category.gender == 'L' and 'Women' in division:
                        fita_results = all_fita_results[fita][division]
                        break

            fita_results_by_entry = {
                result.target.session_entry.competition_entry: result for result in fita_results
            }

            for round, divisions in seeding_results.items():
                for division in divisions:
                    if 'Compound' in str(category.category) and '50m' in round.round.name:
                        if category.category.gender == 'G' and division.gender == 'G':
                            ranking_results = seeding_results[round][division]
                            break
                        if category.category.gender == 'L' and division.gender == 'L':
                            ranking_results = seeding_results[round][division]
                            break
                    if 'Recurve' in str(category.category) and '70m' in round.round.name:
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
                    tiebreak=0,
                    disqualified=False,
                    retired=False,
                    placing=seed.rank,
                ))

            results = sorted(weekend_results, key=lambda s: (s.xs, s.hits, s.golds))
            for i, result in enumerate(results, 1):
                result.placing = i
            full_results[category.category.name] = results

        headers = ['Pl.'] + self.get_main_headers(competition) + ['720', 'H2H', '1440', 'Total']
        section = ResultSection('Weekend results', None, headers)
        return {section: full_results}


def get_result_modes():
    modes = BaseResultMode.__subclasses__()
    modes = sorted(modes, key=lambda m: m.slug)
    return [(mode.slug, mode.name) for mode in modes]


def get_mode(slug, **kwargs):
    modes = BaseResultMode.__subclasses__()
    try:
        return [mode(**kwargs) for mode in modes if mode.slug == slug][0]
    except IndexError:
        return None

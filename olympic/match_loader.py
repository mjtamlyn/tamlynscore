from .models import Match, Seeding


class MatchLoader:
    LEVELS = ['Final', 'Semis', 'Quarters', '1/8', '1/16', '1/32', '1/64', '1/128']
    TIMINGS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    PASSES = 'ABCDEFGHIJK'

    def __init__(self, competition):
        self.competition = competition
        self.matches = []
        self.categories = []
        self.timings = []
        self.passes = []
        self.targets = []
        self.seeding_lookup = {}
        self.max_levels = {}
        self.match_lookup = {}
        self.match_lookup_by_range = {}
        self.match_lookup_by_seed = {}

    def load_all(self):
        self.matches = Match.objects.filter(session_round__session__competition=self.competition).select_related('session_round', 'session_round__shot_round', 'session_round__category').prefetch_related('session_round__category__bowstyles', 'result_set', 'result_set__seed__entry__archer')

        session_rounds = {m.session_round for m in self.matches}
        self.match_lookup = {(m.session_round, m.level, m.match): m for m in self.matches}

        seedings = Seeding.objects.filter(session_round__in=session_rounds).select_related(
            'entry__archer',
        )
        self.seeding_lookup = {(s.session_round_id, s.seed): s for s in seedings}
        self.max_levels = {session_round: max(m.level for m in self.matches if m.session_round == session_round) for session_round in session_rounds}

        self.setup()

    def setup(self):
        for match in self.matches:
            if match.session_round.category not in self.categories:
                self.categories.append(match.session_round.category)
            target = match.target_2 or match.target
            if target not in self.targets:
                self.targets = list(range(1, target + 1))
            if len(self.timings) < match.timing + 1:
                self.timings = self.TIMINGS[:match.timing]
                self.passes = self.PASSES[:match.timing]
                match.pass_label = self.PASSES[match.timing - 1]

            self.match_lookup_by_range[(match.timing, match.target)] = match
            if match.target_2:
                self.match_lookup_by_range[(match.timing, match.target_2)] = match

            if match.result_set.all():
                match.results = list(match.result_set.all())
                if not match.match % 2:
                    match.results.reverse()
                match.seed_1 = match.results[0].seed.seed
                match.archer_1 = match.results[0].seed.entry.archer
                match.score_1 = match.results[0].total
                match.seed_2 = match.results[1].seed.seed
                match.archer_2 = match.results[1].seed.entry.archer
                match.score_2 = match.results[1].total
                match.is_bye = False

                # Fill in next match if we have a result
                if match.results[0].win or match.results[1].win:
                    archer = match.results[0].seed if match.results[0].win else match.results[1].seed
                    seed = archer.seed
                    next_match_number = match.match if match.match <= 2 ** (match.level - 2) else 2 ** (match.level - 1) + 1 - match.match
                    next_match = self.match_lookup[(match.session_round, match.level - 1, next_match_number)]
                    next_match.pre_filled = True
                    effective_seed = Match.objects._effective_seed(seed, match.level - 1)
                    seeds = [next_match_number, (2 ** match.level) + 1 - next_match_number]
                    if next_match_number % 2:
                        seeds.reverse()
                    if match.seed_1:
                        archer = match.archer_1
                    if match.seed_2:
                        archer = match.archer_2
                    if effective_seed == seeds[0]:
                        next_match.archer_1 = archer
                        next_match.seed_1 = seed
                    else:
                        next_match.archer_2 = archer
                        next_match.seed_2 = seed

            elif match.level == self.max_levels[match.session_round] and self.seeding_lookup:
                match.results = []
                seeds = [match.match, (2 ** match.level) + 1 - match.match]
                if not match.match % 2:
                    seeds.reverse()
                seed_1 = self.seeding_lookup.get((match.session_round_id, seeds[0]), None)
                if seed_1:
                    match.seed_1 = seeds[0]
                    match.archer_1 = seed_1.entry.archer
                else:
                    match.seed_1 = None
                    match.archer_1 = 'BYE'
                seed_2 = self.seeding_lookup.get((match.session_round_id, seeds[1]), None)
                if seed_2:
                    match.seed_2 = seed_2.seed
                    match.archer_2 = seed_2.entry.archer
                else:
                    match.seed_2 = None
                    match.archer_2 = 'BYE'
                match.is_bye = False
                if (seed_2 and not seed_1) or (seed_1 and not seed_2):
                    match.is_bye = True
                match.score_1 = match.score_2 = None

                # Fill in next match
                if match.is_bye:
                    seed = match.seed_1 or match.seed_2
                    next_match_number = match.match if match.match <= 2 ** (match.level - 2) else 2 ** (match.level - 1) + 1 - match.match
                    next_match = self.match_lookup[(match.session_round, match.level - 1, next_match_number)]
                    next_match.pre_filled = True
                    seeds = [next_match_number, (2 ** match.level) + 1 - next_match_number]
                    if next_match_number % 2:
                        seeds.reverse()
                    if match.seed_1:
                        archer = match.archer_1
                    if match.seed_2:
                        archer = match.archer_2
                    if seed == seeds[0]:
                        next_match.archer_1 = archer
                        next_match.seed_1 = seed
                    else:
                        next_match.archer_2 = archer
                        next_match.seed_2 = seed

            elif getattr(match, 'pre_filled', False):
                # Fill in some defaults
                match.results = []
                match.is_bye = False
                match.score_1 = match.score_2 = None
                if not hasattr(match, 'seed_1'):
                    match.seed_1 = None
                if not hasattr(match, 'seed_2'):
                    match.seed_2 = None
                if not hasattr(match, 'archer_1'):
                    match.archer_1 = 'TBC'
                if not hasattr(match, 'archer_2'):
                    match.archer_2 = 'TBC'

            else:
                match.results = []
                match.is_bye = False
                seeds = [match.match, (2 ** match.level) + 1 - match.match]
                if not match.match % 2:
                    seeds.reverse()
                match.seed_1, match.seed_2 = seeds
                match.archer_1 = match.archer_2 = 'TBC'
                match.score_1 = match.score_2 = None

    def matches_by_time(self):
        layout = [{
            'name': 'Pass %s' % self.PASSES[timing - 1],
            'targets': []
        } for timing in self.timings]
        for timing in self.timings:
            targets = layout[timing - 1]['targets']
            for target in self.targets:
                match = self.match_lookup_by_range.get((timing, target), None)
                details = {
                    'number': target,
                    'match': match,
                }
                if not match:
                    continue
                details.update({
                    'category': match.session_round.category.name,
                    'distance': match.session_round.shot_round.short_name,
                    'round': self.LEVELS[match.level - 1],
                    'seed_1': match.seed_1,
                    'seed_2': match.seed_2,
                    'archer_1': match.archer_1,
                    'archer_2': match.archer_2,
                    'score_1': match.score_1,
                    'score_2': match.score_2,
                    'is_bye': match.is_bye,
                    'has_second_target': False,
                    'is_second_target': False,
                })
                if match.level == 1 and match.match == 2:
                    details['round'] = 'Bronze'
                if match.target_2:
                    details['has_second_target'] = True
                if match.target_2 and match.target_2 == target:
                    details['archer_1'] = match.archer_2
                    details['seed_1'] = match.seed_2
                    details['score_1'] = match.score_2
                    details['archer_2'] = None
                    details['seed_2'] = None
                    details['score_2'] = None
                    details['is_second_target'] = True
                targets.append(details)
        return layout

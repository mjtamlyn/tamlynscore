from django.http import Http404

from entries.models import ResultsMode

from .models import Score
from .result_modes import get_mode


class ResultModeMixin(object):
    include_distance_breakdown = False
    format = None

    def get_hide_golds(self):
        if self.format == 'big-screen':
            return True
        return False

    def get_scores(self):
        scores = Score.objects.filter(
            target__session_entry__competition_entry__competition=self.competition
        ).select_related(
            'target',
            'target__session_entry',
            'target__session_entry__session_round',
            'target__session_entry__session_round__shot_round',
            'target__session_entry__competition_entry',
            'target__session_entry__competition_entry__competition',
            'target__session_entry__competition_entry__archer',
            'target__session_entry__competition_entry__bowstyle',
            'target__session_entry__competition_entry__club',
        ).order_by(
            '-target__session_entry__competition_entry__age',
            '-target__session_entry__competition_entry__agb_age',
            'target__session_entry__competition_entry__novice',
            'target__session_entry__competition_entry__bowstyle',
            'target__session_entry__competition_entry__archer__gender',
            'disqualified',
            '-score',
            '-is_actual_zero',
            '-golds',
            '-xs'
        )
        return scores

    def get_mode(self, mode_name=None, load=False):
        if mode_name is None:
            mode_name = self.kwargs['mode']
        mode = get_mode(mode_name, include_distance_breakdown=self.include_distance_breakdown, hide_golds=self.get_hide_golds())
        if not mode:
            raise Http404('No such mode')
        if load:
            exists, obj = self.mode_exists(mode, load=True)
        else:
            exists = self.mode_exists(mode)
        if not exists:
            raise Http404('No such mode for this competition')
        return (mode, obj) if load else mode

    def mode_exists(self, mode, load=False):
        if load:
            try:
                obj = self.competition.result_modes.filter(mode=mode.slug).get()
            except ResultsMode.DoesNotExist:
                return False, None
            else:
                return True, obj
        else:
            return self.competition.result_modes.filter(mode=mode.slug).exists()

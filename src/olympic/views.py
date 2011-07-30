from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import render, get_object_or_404

from entries.models import Competition
from scores.models import Score
from olympic.models import OlympicSessionRound, Seeding

from itertools import groupby

class OlympicIndex(View):
    def get(self, request, slug):
        competition = get_object_or_404(Competition, slug=slug)
        session_rounds = OlympicSessionRound.objects.filter(session__competition=competition).order_by('session__start')
        session_info = [(
            session_round.session,
            session_round,
            session_round.seeding_set.all(),
            Score.objects.results(session_round.ranking_round, leaderboard=False, category=session_round.category),
        ) for session_round in session_rounds]
        sessions = []
        for key, values in groupby(session_info, lambda x: x[0]):
            sessions.append((key, [value[1] for value in values]))

        if 'remove-all' in request.GET:
            Seeding.objects.filter(session_round__pk=request.GET['remove-all']).delete()
        return render(request, 'olympic_index.html', locals())

    def post(self, request, slug):
        session_round = OlympicSessionRound.objects.get(pk=request.POST['form-id'].replace('confirm-seedings-', ''))
        score_ids = map(lambda s: int(s.replace('score-', '')), filter(lambda s: s.startswith('score-'), request.POST))
        scores = Score.objects.filter(pk__in=score_ids)
        session_round.set_seedings(scores)
        return self.get(request, slug)

olympic_index = login_required(OlympicIndex.as_view())


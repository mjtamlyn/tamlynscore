from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import View

from records.models import *
from records.forms import *

def index(request):
    competitions = Competition.objects.all()
    return render_to_response('index.html', locals(), context_instance=RequestContext(request))

def competition_index(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    results = competition.full_results()
    return render_to_response('competition_index.html', locals(), context_instance=RequestContext(request))

class AddScoresView(View):
    def get(self, request, round_id):
        the_round = get_object_or_404(BoundRound, id=round_id)
        form = ScoreEntryForm()
        return render_to_response('add_scores.html', locals(), context_instance=RequestContext(request))

    def post(self, request, round_id):
        the_round = get_object_or_404(BoundRound, id=round_id)
        form = ScoreEntryForm(request.POST)
        if form.is_valid():
            score = form.save(commit=False)
            score.shot_round = the_round
            score.save()
            form = ScoreEntryForm()
        return render_to_response('add_scores.html', locals(), context_instance=RequestContext(request))


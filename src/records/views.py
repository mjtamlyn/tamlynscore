from django.db.models import Sum
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
        form = ScoreEntryForm(initial={'hits': the_round.round_type.subrounds.aggregate(Sum('arrows'))['arrows__sum']})
        return render_to_response('add_scores.html', locals(), context_instance=RequestContext(request))

    def post(self, request, round_id):
        the_round = get_object_or_404(BoundRound, id=round_id)
        entry = Entry(shot_round=the_round)
        form = ScoreEntryForm(request.POST, instance=entry)
        if form.is_valid():
            score = form.save()
            return self.get(request, round_id)
        return render_to_response('add_scores.html', locals(), context_instance=RequestContext(request))

class NewClubView(View):
    def get(self, request):
        form = ClubForm()
        return render_to_response('new_club.html', locals(), context_instance=RequestContext(request))

    def post(self, request):
        form = ClubForm(request.POST)
        if form.is_valid():
            form.save()
            return self.get(request)
        return render_to_response('new_club.html', locals(), context_instance=RequestContext(request))


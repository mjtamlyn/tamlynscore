from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import View

from records.models import *
from records.forms import *

from itertools import groupby
import math

def index(request):
    competitions = Competition.objects.all()
    return render_to_response('index.html', locals(), context_instance=RequestContext(request))

def competition_index(request, slug):
    competition = get_object_or_404(Competition, slug=slug)
    results = competition.full_results()
    return render_to_response('competition_index.html', locals(), context_instance=RequestContext(request))

class AddScoresView(View):
    def get(self, request, round_id):
        the_round = get_object_or_404(BoundRound, pk=round_id)
        competition = the_round.competition
        form = ScoreEntryForm(initial={'hits': the_round.arrows})
        return render_to_response('add_scores.html', locals(), context_instance=RequestContext(request))

    def post(self, request, round_id):
        the_round = get_object_or_404(BoundRound, pk=round_id)
        competition = the_round.competition
        entry = Entry(shot_round=the_round)
        form = ScoreEntryForm(request.POST, instance=entry)
        if form.is_valid():
            score = form.save()
            return self.get(request, round_id)
        return render_to_response('add_scores.html', locals(), context_instance=RequestContext(request))
add_scores = AddScoresView.as_view()

def add_arrow_values_index(request, round_id):
    the_round = get_object_or_404(BoundRound, pk=round_id, use_individual_arrows=True)
    dozens = int(math.ceil(the_round.arrows/12))
    dozens = range(1, 1 + dozens)
    entries = Entry.objects.filter(shot_round=the_round)
    targets = []
    for key, group in groupby(entries, lambda e: e.target[:-1]):
        targets.append({
            'target': int(key),
            'archers': list(group)
        })
    if request.GET.get('fd', ''):
        highlighted = {
            'dozen': int(request.GET['fd']),
            'target': int(request.GET['ft']) + 1,
        }
    return render_to_response('add_arrow_values_index.html', locals(), context_instance=RequestContext(request))

class AddArrowValuesView(View):
    def get(self, request, round_id, target_no, doz_no):
        the_round = get_object_or_404(BoundRound, pk=round_id, use_individual_arrows=True)
        forms = get_arrow_formset(the_round, target_no, doz_no)
        return render_to_response('add_arrow_values.html', locals(), context_instance=RequestContext(request))

    def post(self, request, round_id, target_no, doz_no):
        the_round = get_object_or_404(BoundRound, pk=round_id, use_individual_arrows=True)
        forms = get_arrow_formset(the_round, target_no, doz_no, data=request.POST)
        arrows = []
        failed = False
        for archer in forms:
            for form in archer['forms']:
                if form.is_valid():
                    arrows.append(form.save(commit=False))
                else:
                    failed = True
        if not failed:
            for arrow in arrows:
                arrow.save()
                arrow.entry.update_totals()
            return HttpResponseRedirect('../../../../?fd={0}&ft={1}#dozen-{0}'.format(doz_no, target_no))
        return render_to_response('add_arrow_values.html', locals(), context_instance=RequestContext(request))
add_arrow_values = AddArrowValuesView.as_view()

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
new_club = NewClubView.as_view()


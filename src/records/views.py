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
    def get(self, request, competition_id):
        form = ScoreEntryForm(initial={'competition': competition_id})
        return render_to_response('add_scores.html', locals(), context_instance=RequestContext(request))

    def post(self, request, competition_id):
        form = ScoreEntryForm(request.POST, initial={'competition': competition_id})
        print form.is_valid()
        return render_to_response('add_scores.html', locals(), context_instance=RequestContext(request))


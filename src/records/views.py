from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from records.models import *

def index(request):
    competitions = Competition.objects.all()
    return render_to_response('index.html', locals(), context_instance=RequestContext(request))

def competition_index(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    results = competition.full_results()
    return render_to_response('competition_index.html', locals(), context_instance=RequestContext(request))

from django.shortcuts import render_to_response, get_object_or_404

from records.models import *

def index(request):
    competitions = Competition.objects.all()
    return render_to_response('index.html', locals())

def competition_index(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    results = competition.full_results()
    return render_to_response('competition_index.html', locals())

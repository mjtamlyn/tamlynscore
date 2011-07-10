from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import render, get_object_or_404

from entries.forms import new_entry_form_for_competition
from entries.models import Tournament, Competition, CompetitionEntry

@login_required
def tournaments(request):
    tournaments = Tournament.objects.all()
    return render(request, 'tournaments.html', locals())

@login_required
def competition_index(request, slug):
    competition = get_object_or_404(Competition, slug=slug)
    return render(request, 'competition_index.html', locals())

class EntriesView(View):
    template = 'competition_entries.html'
    category = Competition
    model = CompetitionEntry

    def render(self, context):
        return render(self.request, self.template, context)

    def get_object(self, slug):
        return get_object_or_404(self.category, slug=slug)

    def get_form_class(self, competition):
        return new_entry_form_for_competition(competition)

    def get(self, request, slug):
        competition = self.get_object(slug)
        entries = competition.competitionentry_set.all()
        form = self.get_form_class(competition)()
        return self.render(locals())

    def post(self, request, slug):
        competition = self.get_object(slug)
        instance = self.model(competition=competition)
        form = self.get_form_class(competition)(request.POST, instance=instance)
        if form.is_valid():
            inst = form.save()
        else:
            print form.errors
        return HttpResponse('ok')

entries = login_required(EntriesView.as_view())

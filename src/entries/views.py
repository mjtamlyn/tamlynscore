from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View
from django.shortcuts import render, get_object_or_404

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch

from entries.forms import new_entry_form_for_competition
from entries.models import *

import json
from itertools import groupby

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

    def get_stats(self, competition):
        stats = []
        stats.append(
            ('Total Entries', competition.competitionentry_set.count()),
        )
        for session in competition.sessions_with_rounds():
            stats.append((
                'Entries for {0}'.format(session.start.strftime('%A')),
                competition.competitionentry_set.filter(sessionentry__session_round__session=session).count(),
            ))
        for session in competition.sessions_with_rounds():
            for session_round in session.sessionround_set.all():
                stats.append((
                    'Entries for {0}'.format(session_round.shot_round),
                    competition.competitionentry_set.filter(sessionentry__session_round=session_round).count(),
                ))
        return stats

    def get(self, request, slug):
        competition = self.get_object(slug)
        entries = competition.competitionentry_set.all().order_by('-pk')
        stats = self.get_stats(competition)
        form = self.get_form_class(competition)()
        return self.render(locals())

    def post(self, request, slug):
        if '_method' in request.POST and request.POST['_method'] == 'delete':
            return self.delete(request, slug)
        competition = self.get_object(slug)
        instance = self.model(competition=competition)
        form = self.get_form_class(competition)(request.POST, instance=instance)
        if form.is_valid():
            entry = form.save()
            return render(request, 'includes/entry_row.html', locals())
        else:
            errors = json.dumps(form.errors)
        return HttpResponseBadRequest(errors)

    def delete(self, request, slug):
        entry = get_object_or_404(self.model, pk=request.POST['pk'])
        entry.delete()
        return HttpResponse('deleted')

entries = login_required(EntriesView.as_view())

class TargetListView(View):
    def get(self, request, slug):
        competition = get_object_or_404(Competition, slug=slug)
        session_rounds = SessionRound.objects.filter(session__competition=competition).order_by('session__start')
        target_list = [(
            session_round.session, # session
            session_round, # round
            session_round.target_list(), # target_list
            session_round.sessionentry_set.annotate(entered=Count('targetallocation')).filter(entered=0), # entries
            ) for session_round in session_rounds]
        sessions = []
        for key, values in groupby(target_list, lambda x: x[0]):
            sessions.append((key, [value[1] for value in values]))
        return render(request, 'target_list.html', locals())

    def post(self, request, slug):
        targets = json.loads(request.POST['targets'])
        for target in targets:
            TargetAllocation.objects.filter(session_entry__pk=target['entry']).delete()
            entry = SessionEntry.objects.get(pk=target['entry'])
            new_allocation = TargetAllocation(session_entry=entry, boss=target['target'][:-1], target=target['target'][-1])
            new_allocation.save()
        return HttpResponse()

target_list = login_required(TargetListView.as_view())

def target_list_pdf(request, slug):
    competition = get_object_or_404(Competition, slug=slug)

    session_rounds = SessionRound.objects.filter(session__competition=competition).order_by('session__start')

    PAGE_HEIGHT=defaultPageSize[1]
    PAGE_WIDTH=defaultPageSize[0]
    styles = getSampleStyleSheet()

    doc_elements = []

    for session_round in session_rounds:
        target_list = session_round.target_list()

        title = "Target List for {0}".format(session_round)
        header = Paragraph(title, styles['Title'])
        table = Table(target_list)
        spacer = Spacer(PAGE_WIDTH, 0.5*inch)

        doc_elements += [header, spacer, table, PageBreak()]

    response = HttpResponse(mimetype='application/pdf')
    doc = SimpleDocTemplate(response)
    doc.build(doc_elements)

    return response

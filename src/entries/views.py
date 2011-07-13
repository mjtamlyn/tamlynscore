from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View
from django.shortcuts import render, get_object_or_404

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, PageBreak, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib import colors
from reportlab.lib.units import inch

from entries.forms import new_entry_form_for_competition
from entries.models import *

from itertools import groupby
import json
import math

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

styles = getSampleStyleSheet()
def para(string, style='Normal'):
    return Paragraph(unicode(string), styles[style])

def target_list_pdf(request, slug):
    competition = get_object_or_404(Competition, slug=slug)

    session_rounds = SessionRound.objects.filter(session__competition=competition).order_by('session__start')

    PAGE_HEIGHT=defaultPageSize[1]
    PAGE_WIDTH=defaultPageSize[0]

    styles['h2'].alignment = 1

    main_title = para(u'{0}: Target List'.format(competition), 'Title')
    doc_elements = [main_title]

    for session_round in session_rounds:
        target_list = session_round.target_list_pdf()

        title = "Target List for {0} - {1}".format(session_round.shot_round, session_round.session.start.strftime('%A, %d %B %Y, %X'))
        header = para(title, 'h2')
        table = Table(target_list)
        spacer = Spacer(PAGE_WIDTH, 0.5*inch)

        doc_elements += [header, spacer, table, PageBreak()]

    response = HttpResponse(mimetype='application/pdf')
    doc = SimpleDocTemplate(response)
    doc.build(doc_elements)

    return response

def score_sheets(request, slug):
    competition = get_object_or_404(Competition, slug=slug)
    rounds = SessionRound.objects.filter(session__competition=competition)
    return render(request, 'score_sheets.html', locals())

def score_sheets_pdf(request, slug, round_id):
    competition = get_object_or_404(Competition, slug=slug)
    session_round = get_object_or_404(SessionRound, pk=round_id)
    shot_round = session_round.shot_round
    subrounds = shot_round.subrounds.order_by('-distance')

    PAGE_HEIGHT=defaultPageSize[1]
    PAGE_WIDTH=defaultPageSize[0]

    def draw_title(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 18)
        canvas.drawCentredString(PAGE_WIDTH/2.0, PAGE_HEIGHT-58, u'{0}: {1}'.format(competition, shot_round))
        canvas.restoreState()

    table_style = TableStyle([
        # alignment
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # arrows grid
        ('BOX', (0, 1), (-1, -2), 2, colors.black),
        ('INNERGRID', (0, 1), (-1, -2), 0.25, colors.black),

        # end totals columns
        ('BOX', (6, 0), (6, -2), 2, colors.black),
        ('BOX', (13, 0), (13, -2), 2, colors.black),

        # totals grid
        ('BOX', (14, 0), (-1, -2), 2, colors.black),
        ('BOX', (14, -1), (-2, -1), 2, colors.black),
        ('LINEBEFORE', (15, 0), (-1, -1), 1.5, colors.black),
    ])

    box_size = 0.35*inch
    wide_box = box_size*1.35
    total_cols = 12 + 2 + 5
    col_widths = 6*[box_size] + [wide_box] + 6*[box_size] + 6*[wide_box]
    spacer = Spacer(PAGE_WIDTH, box_size*0.4)
    score_sheet_elements = []
    for subround in subrounds:
        subround_title = para(u'{0}{1}'.format(subround.distance, subround.unit), 'h3')
        dozens = subround.arrows / 12
        total_rows = dozens + 2
        table_data = [[subround_title] + [None] * 5 + ['ET'] + [None] * 6 + ['ET', 'DT', 'H', 'G', 'X', 'RT']]
        table_data += [[None for i in range(total_cols)] for j in range(total_rows - 1)]
        table = Table(table_data, col_widths, total_rows*[box_size])
        table.setStyle(table_style)

        score_sheet_elements += [table, spacer]

    compound_round = bool(subrounds.count() - 1)
    if compound_round:
        table_style = TableStyle([
            ('BOX', (14, 0), (-2, 0), 2, colors.black),
            ('LINEBEFORE', (15, 0), (-1, -1), 1.5, colors.black),
        ])
        totals_table = Table([[None]*total_cols], col_widths, [box_size])
        totals_table.setStyle(table_style)

        score_sheet_elements += [totals_table, spacer]

    signing_table_widths = [0.7*inch, 2*inch]
    signing_table = Table([[para('Archer', 'h3'), None, None, para('Scorer', 'h3'), '']], signing_table_widths + [0.5*inch] + signing_table_widths)
    signing_table.setStyle(TableStyle([
        ('LINEBELOW', (1, 0), (1, 0), 1, colors.black),
        ('LINEBELOW', (4, 0), (4, 0), 1, colors.black),
    ]))
    score_sheet_elements += [spacer, signing_table, spacer]

    doc_elements = []
    for boss, entries in groupby(session_round.target_list(), lambda x: x[0][:-1]):
        for target, entry in entries:
            if entry:
                entry = entry.session_entry.competition_entry
                table_data = [
                        [para(target, 'h2'), para(entry.archer, 'h2'), para(entry.club.name, 'h2')],
                        [None, para(u'{0} {1}'.format(entry.archer.get_gender_display(), entry.bowstyle), 'h2'), para(entry.get_age_display(), 'h2')],
                ]
            else:
                table_data = [
                        [para(target, 'h2'), None, None],
                        [None],
                ]
            header_table = Table(table_data, [0.5*inch, 3*inch, 3*inch])
            doc_elements.append(KeepTogether([header_table, spacer] + score_sheet_elements))
        doc_elements.append(PageBreak())

    response = HttpResponse(mimetype='application/pdf')
    doc = SimpleDocTemplate(response)
    doc.build(doc_elements, onFirstPage=draw_title, onLaterPages=draw_title)

    return response


import collections
import copy
import functools
import itertools
import json
import math
import re

from django.core.cache import cache
from django.db.models import Prefetch
from django.http import (
    Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    DeleteView, DetailView, FormView, ListView, TemplateView, UpdateView, View,
)

from braces.views import MessageMixin, SuperuserRequiredMixin
from render_block import render_block_to_string
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
    TableStyle,
)
from reportlab.rl_config import defaultPageSize

from core.models import Archer
from scores.mixins import ResultModeMixin

from .forms import (
    ArcherSearchForm, CompetitionForm, CSVEntryForm, EntryCreateForm,
    EntryUpdateForm,
)
from .models import (
    SCORING_DOZENS, SCORING_FULL, Competition, CompetitionEntry, EntryUser,
    Session, SessionEntry, SessionRound, TargetAllocation,
)


class CompetitionList(ListView):
    model = Competition

    def get_queryset(self):
        qs = super(CompetitionList, self).get_queryset()
        return qs.select_related('tournament').order_by('-date')

    def get_context_data(self):
        context = super(CompetitionList, self).get_context_data()
        today = timezone.now().date()
        context['upcoming'] = context['object_list'].filter(date__gt=today).order_by('date')
        context['current'] = context['object_list'].filter(date__lte=today, end_date__gte=today)
        context['past'] = context['object_list'].filter(end_date__lt=today)
        return context


class CompetitionCreate(SuperuserRequiredMixin, FormView):
    form_class = CompetitionForm
    template_name = 'entries/competition_form.html'

    def form_valid(self, form):
        self.competition = form.save()
        return super(CompetitionCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('competition_detail', kwargs={'slug': self.competition.slug})


class CompetitionMixin(MessageMixin):
    admin_required = True

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.competition = get_object_or_404(Competition, slug=kwargs['slug'])
        self.is_admin = self.competition.is_admin(self.request.user)

    def check_permission(self):
        return self.is_admin or not self.admin_required

    def dispatch(self, request, *args, **kwargs):
        if not self.check_permission():
            self.messages.error('You must be logged in as a competition admin to do that.')
            return HttpResponseRedirect(reverse('competition_detail', kwargs={'slug': self.kwargs['slug']}))
        return super().dispatch(request, *args, **kwargs)

    def get_meta_description(self):
        return '{} on {}, hosted on TamlynScore.'.format(self.competition, self.competition.date.strftime('%d %B %Y'))

    def get_context_data(self, **kwargs):
        context = super(CompetitionMixin, self).get_context_data(**kwargs)
        context.update({
            'competition': self.competition,
            'competition_admin': self.is_admin,
            'title': str(self.competition),
            'meta_description': self.get_meta_description(),
        })
        return context


class CompetitionDetail(CompetitionMixin, ResultModeMixin, DetailView):
    admin_required = False
    object_name = 'competition'

    def get_object(self):
        return self.competition

    def get_result_mode(self, mode):
        pass

    def get_context_data(self, **kwargs):
        today = timezone.now().date()

        context = super().get_context_data(**kwargs)
        context['legs'] = self.object.leg_set.select_related('season__league')
        context['related_events'] = self.object.tournament.competition_set.order_by('-date').exclude(pk=self.object.pk)

        context['is_future'] = (self.competition.date > today)
        if context['is_future']:
            rounds = set()
            for session in self.competition.session_set.all():
                rounds |= {sr.shot_round for sr in session.sessionround_set.all()}
            context['rounds'] = {r.pk: {
                'round': r,
                'entry_count': 0,
                'entries': [],
            } for r in rounds}

            entries = SessionEntry.objects.filter(
                competition_entry__competition=self.competition
            ).select_related(
                'session_round',
                'competition_entry',
                'competition_entry__bowstyle',
                'competition_entry__archer',
            )
            for entry in entries:
                context['rounds'][entry.session_round.shot_round_id]['entry_count'] += 1
                context['rounds'][entry.session_round.shot_round_id]['entries'].append(entry)

            for info in context['rounds'].values():
                if self.competition.has_agb_age_groups:
                    if self.competition.has_novices:
                        counter = collections.Counter('%s %s %s%s' % (
                            e.competition_entry.bowstyle,
                            e.competition_entry.get_agb_age_display(),
                            e.competition_entry.get_gender_display(),
                            (' %s' % e.competition_entry.get_novice_display()) if e.competition_entry.novice == 'N' else '',
                        ) for e in info['entries'])
                    else:
                        counter = collections.Counter('%s %s %s' % (
                            e.competition_entry.bowstyle,
                            e.competition_entry.get_agb_age_display(),
                            e.competition_entry.get_gender_display(),
                        ) for e in info['entries'])
                else:
                    if self.competition.has_novices:
                        counter = collections.Counter('%s %s%s' % (
                            e.competition_entry.bowstyle,
                            e.competition_entry.get_gender_display(),
                            (' %s' % e.competition_entry.get_novice_display()) if e.competition_entry.novice == 'N' else '',
                        ) for e in info['entries'])
                    else:
                        counter = collections.Counter('%s %s' % (
                            e.competition_entry.bowstyle,
                            e.competition_entry.get_gender_display(),
                        ) for e in info['entries'])
                info['data'] = counter.most_common(10)
            context['rounds'] = sorted(context['rounds'].values(), key=lambda r: -r['round'].longest_distance)
            context['entry_count'] = self.competition.competitionentry_set.count()

            context['target_list_set'] = TargetAllocation.objects.filter(
                session_entry__competition_entry__competition=self.competition,
            ).exists()
        else:
            try:
                by_round = self.get_mode('by-round')
            except Http404:
                by_round = None
            if by_round:
                context['by_round'] = by_round.get_results(self.competition, self.get_scores(), leaderboard=True, request=self.request)
                for section in context['by_round']:
                    for category in context['by_round'][section]:
                        for score in context['by_round'][section][category]:
                            score.details = by_round.score_details(score, section)
        return context


class CompetitionUpdate(CompetitionMixin, FormView):
    form_class = CompetitionForm
    template_name = 'entries/competition_form.html'

    def get_form_kwargs(self):
        kwargs = super(CompetitionUpdate, self).get_form_kwargs()
        kwargs['instance'] = self.competition
        return kwargs

    def form_valid(self, form):
        self.competition = form.save()
        return super(CompetitionUpdate, self).form_valid(form)

    def get_success_url(self):
        return reverse('competition_detail', kwargs={'slug': self.competition.slug})


class EntryList(CompetitionMixin, ListView):
    model = CompetitionEntry
    template_name = 'entries/entry_list.html'

    def get_queryset(self):
        return self.model.objects.filter(
            competition=self.competition,
        ).select_related(
            'competition',
            'club',
            'bowstyle',
            'archer',
        ).prefetch_related(
            Prefetch(
                'sessionentry_set',
                queryset=SessionEntry.objects.select_related(
                    'session_round__session',
                    'session_round__shot_round',
                ),
            )
        ).order_by('-pk')

    def get_stats(self):
        competition = self.competition
        stats = []
        sessions = competition.session_set.prefetch_related(
            'sessionround_set',
            Prefetch(
                'sessionround_set__sessionentry_set',
                queryset=SessionEntry.objects.select_related(
                    'competition_entry',
                    'competition_entry__archer',
                ).prefetch_related(
                    'competition_entry__bowstyle',
                    'competition_entry__competition',
                ),
            ),
        ).order_by('start')
        for session in sessions:
            session_rounds = session.sessionround_set.all()
            session_round_stats = []
            for sr in session_rounds:
                bowstyles = collections.Counter(e.competition_entry.bowstyle for e in sr.sessionentry_set.all())
                genders = collections.Counter(
                    e.competition_entry.get_gender_display() for e in sr.sessionentry_set.all())
                session_round_stats.append({
                    'session_round': sr,
                    'total_entries': len(sr.sessionentry_set.all()),
                    'bowstyles': bowstyles.most_common(5),
                    'genders': genders.most_common(2),
                })
                if competition.has_novices:
                    session_round_stats[-1]['novice_count'] = len([e for e in sr.sessionentry_set.all() if e.competition_entry.novice == 'N'])
                if competition.has_juniors:
                    session_round_stats[-1]['junior_count'] = len([e for e in sr.sessionentry_set.all() if e.competition_entry.age == 'J'])
                if competition.has_agb_age_groups:
                    session_round_stats[-1]['agb_age_groups'] = collections.Counter(
                        e.competition_entry.get_agb_age_display() for e in
                        sr.sessionentry_set.all() if e.competition_entry.agb_age
                    ).most_common(5)
                if competition.ifaa_rules:
                    session_round_stats[-1]['ifaa_division'] = collections.Counter(
                        e.competition_entry.get_ifaa_division_display() for e in sr.sessionentry_set.all()
                    ).most_common(7)
            stats.append({
                'session': session,
                'total_entries': SessionEntry.objects.filter(session_round__session=session).count(),
                'session_rounds': session_round_stats,
            })
        return stats

    def get_context_data(self, **kwargs):
        context = super(EntryList, self).get_context_data(**kwargs)
        context['stats'] = self.get_stats()
        context['search_form'] = ArcherSearchForm()
        return context


class BatchEntryMixin(object):
    BATCH_KEY = 'batch'

    def get_context_data(self, **kwargs):
        context = super(BatchEntryMixin, self).get_context_data(**kwargs)
        context['batch'] = self.is_in_batch()
        if context['batch']:
            context['current_row'] = ', '.join('%s: %s' % item for item in self.get_batch()[0].items())
            context['batch_length'] = len(self.get_batch())
        return context

    def is_in_batch(self):
        return self.BATCH_KEY in self.request.session

    def get_batch(self):
        return self.request.session[self.BATCH_KEY]

    def url_for_next_in_batch(self):
        next_name = self.get_batch()[0]['name']
        url = reverse('archer_search', kwargs={'slug': self.competition.slug})
        return url + '?query=' + next_name


class BatchEntryStart(BatchEntryMixin, CompetitionMixin, FormView):
    form_class = CSVEntryForm
    template_name = 'entries/batch_entry_start.html'

    def form_valid(self, form):
        self.request.session[self.BATCH_KEY] = form.read_data
        return super(BatchEntryStart, self).form_valid(form)

    def get_success_url(self):
        return self.url_for_next_in_batch()


class ArcherSearch(BatchEntryMixin, CompetitionMixin, TemplateView):
    template_name = 'entries/archer_search.html'

    def get(self, request, *args, **kwargs):
        if self.request.GET:
            search_form = ArcherSearchForm(self.request.GET)
            archers = []
            if search_form.is_valid():
                archers = search_form.get_archers()
        else:
            search_form = ArcherSearchForm()
            archers = []
        context = self.get_context_data(
            search_form=search_form,
            archers=archers,
        )
        return self.render_to_response(context)


class EntryAdd(BatchEntryMixin, CompetitionMixin, DetailView):
    model = Archer
    pk_url_kwarg = 'archer_id'
    template_name = 'entries/entry_add.html'

    def get_initial(self):
        initial = {}
        if self.is_in_batch():
            initial.update(self.get_batch()[0])
        return initial

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = EntryCreateForm(
            archer=self.object,
            competition=self.competition,
            initial=self.get_initial(),
        )
        context = self.get_context_data(
            form=form,
        )
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = EntryCreateForm(
            data=self.request.POST,
            competition=self.competition,
            archer=self.object,
        )
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            context = self.get_context_data(form=form)
            return self.render_to_response(context)

    def get_success_url(self):
        if self.is_in_batch():
            batch = self.request.session[self.BATCH_KEY][1:]
            if batch:
                self.request.session[self.BATCH_KEY] = batch
                return self.url_for_next_in_batch()
            else:
                del self.request.session[self.BATCH_KEY]
        return reverse('entry_list', kwargs={'slug': self.competition.slug})


class EntryUpdate(CompetitionMixin, UpdateView):
    model = CompetitionEntry
    pk_url_kwarg = 'entry_id'
    template_name = 'entries/entry_update.html'
    form_class = EntryUpdateForm

    def get_form_kwargs(self):
        kwargs = super(EntryUpdate, self).get_form_kwargs()
        kwargs['competition'] = self.competition
        return kwargs

    def get_success_url(self):
        return reverse('entry_list', kwargs={'slug': self.competition.slug})


class EntryDelete(CompetitionMixin, DeleteView):
    model = CompetitionEntry
    pk_url_kwarg = 'entry_id'
    template_name = 'entries/entry_delete.html'

    def get_success_url(self):
        return reverse('entry_list', kwargs={'slug': self.competition.slug})


class TargetList(CompetitionMixin, ListView):
    template_name = 'entries/target_list.html'
    model = TargetAllocation
    admin_required = False
    editable = False

    def get_queryset(self):
        return self.model.objects.filter(
            session_entry__competition_entry__competition=self.competition,
        ).select_related(
            'session_entry__competition_entry__competition__tournament',
            'session_entry__session_round__session',
            'session_entry__session_round__shot_round',
            'session_entry__competition_entry__bowstyle',
            'session_entry__competition_entry__club',
            'session_entry__competition_entry__archer',
            'session_entry__competition_entry__archer__bowstyle',
            'session_entry__competition_entry__archer__club',
        )

    def get_empty_target_list(self):
        target_list = collections.OrderedDict()
        session_rounds = SessionRound.objects.filter(
            session__competition__slug=self.kwargs['slug'],
        ).select_related('session').order_by('session__start')
        for session_round in session_rounds:
            session = session_round.session
            if session not in target_list:
                target_list[session] = {'rounds': [session_round], 'targets': [], 'entries': []}
            else:
                target_list[session]['rounds'].append(session_round)
        return target_list

    def get_target_list(self):
        target_list = self.get_empty_target_list()
        for allocation in self.allocations:
            session_round = allocation.session_entry.session_round
            session = session_round.session
            target_list[session]['targets'].append(allocation)

        # Turn the targets into an actual target list
        for session, options in target_list.items():
            details = session.details
            # Work out which bosses and details we need
            archers_per_target = session.archers_per_target
            allocations = options['targets']
            num_entries = SessionEntry.objects.filter(session_round__session=session).count()
            current_bosses = [allocation.boss for allocation in allocations]
            min_boss = min(current_bosses) if current_bosses else 1
            needed_bosses = int(math.ceil(num_entries / float(archers_per_target)))
            current_max_boss = max(current_bosses) if current_bosses else 1
            bosses = range(min_boss, max(needed_bosses, current_max_boss) + 1)

            # Make a lookup dictionary from the current allocations
            allocations_lookup = dict([
                ('{0}{1}'.format(allocation.boss, allocation.target), allocation) for allocation in allocations
            ])

            session_target_list = options['target_list'] = []

            for boss in bosses:
                allocations = []
                for detail in details:
                    target = '{0}{1}'.format(boss, detail)
                    allocations.append((detail, allocations_lookup.get(target, None)))
                session_target_list.append((boss, allocations))
        return target_list

    def add_unallocated_entries(self, target_list):
        entries = SessionEntry.objects.filter(
            competition_entry__competition=self.competition
        ).exclude(targetallocation__isnull=False).select_related(
            'session_round__session',
            'competition_entry__club',
            'competition_entry__county',
            'competition_entry__archer',
            'competition_entry__bowstyle'
        )

        for entry in entries:
            session = entry.session_round.session
            target_list[session]['entries'].append(entry)

        for details in target_list.values():
            details['entries'] = sorted(details['entries'], key=lambda e: (
                e.session_round.shot_round_id,
                e.competition_entry.bowstyle.name,
                e.competition_entry.team_name(),
                e.competition_entry.archer.gender,
                e.competition_entry.age,
                e.competition_entry.novice,
                e.competition_entry.archer.name,
            ))
            data = [self.get_json_data(e) for e in details['entries']]
            details['entries_json'] = json.dumps(data)

    def get_json_data(self, entry):
        data = {
            'id': entry.pk,
            'name': entry.competition_entry.archer.name,
            'gender': entry.competition_entry.get_gender_display(),
            'bowstyle': entry.competition_entry.bowstyle.name,
            'club': entry.competition_entry.team_name(),
            'text': u'%s %s %s %s' % (
                entry.competition_entry.archer,
                entry.competition_entry.club,
                entry.competition_entry.bowstyle,
                entry.competition_entry.archer.get_gender_display(),
            )
        }
        if self.competition.has_novices and entry.competition_entry.novice == 'N':
            data['novice'] = entry.competition_entry.get_novice_display()
        if self.competition.has_juniors and entry.competition_entry.age == 'J':
            data['age'] = entry.competition_entry.get_age_display()
        return data

    def get_context_data(self, **kwargs):
        context = super(TargetList, self).get_context_data(**kwargs)
        self.allocations = context['object_list']

        if self.allocations:
            self.competition = self.allocations[0].session_entry.competition_entry.competition
        else:
            self.competition = Competition.objects.get(slug=self.kwargs['slug'])

        target_list = self.get_target_list()
        self.add_unallocated_entries(target_list)

        context.update({
            'target_list': target_list,
            'editable': self.editable,
        })
        return context


class TargetListEdit(TargetList):
    template_name = 'entries/target_list_edit.html'
    admin_required = True
    editable = True

    def post(self, request, slug):
        data = json.loads(request.body.decode('utf-8'))
        if data['method'] == 'create':
            allocation = TargetAllocation.objects.create(
                session_entry_id=data['entry'],
                boss=data['location'][:-1],
                target=data['location'][-1]
            )
            return HttpResponse(allocation.pk)
        elif data['method'] == 'delete':
            TargetAllocation.objects.get(session_entry__id=data['session_entry']).delete()
            return HttpResponse('ok')
        return HttpResponseBadRequest()


class Registration(TargetList):
    template_name = 'entries/registration.html'
    admin_required = True

    def add_unallocated_entries(self, target_list):
        pass

    def get_target_list(self):
        target_list = super(Registration, self).get_target_list()
        for session, entries in target_list.items():
            unregistered = 0
            for target in target_list[session]['targets']:
                if not target.session_entry.present:
                    unregistered += 1
                try:
                    entry_user = target.session_entry.competition_entry.entryuser
                except EntryUser.DoesNotExist:
                    entry_user = EntryUser.objects.create(competition_entry=target.session_entry.competition_entry)
                target.login_url = self.request.build_absolute_uri(reverse('entry-authenticate', kwargs={
                    'id': entry_user.uuid,
                }))
            target_list[session]['unregistered'] = unregistered
        return target_list

    def render_to_response(self, context, **response_kwargs):
        if self.request.POST.get('pjax'):
            response = render_block_to_string(
                self.get_template_names(),
                'judge_content',
                context,
            )
            return HttpResponse(response)
        return super().render_to_response(context, **response_kwargs)

    def post(self, request, slug):
        present = request.POST['present'] == 'true'
        updated = SessionEntry.objects.filter(pk=request.POST['pk']).update(present=present)
        if not updated:
            raise Http404
        session_entry = SessionEntry.objects.get(pk=request.POST['pk'])
        cache.delete('bosses_cache_%d' % session_entry.session_round.session_id)
        return HttpResponse('ok')


class ScoreSheets(CompetitionMixin, ListView):
    template_name = 'entries/score_sheets.html'

    def get_queryset(self):
        return SessionRound.objects.filter(
            session__competition=self.competition,
        ).select_related('session', 'shot_round', 'session__competition__tournament').order_by('session__start', 'shot_round_id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        by_session = collections.OrderedDict()
        for sr in self.object_list:
            if sr.session in by_session:
                by_session[sr.session].append(sr)
            else:
                by_session[sr.session] = [sr]
        context['by_session'] = by_session
        return context


# PDF views

class PdfView(View):
    filename = None

    styles = getSampleStyleSheet()
    PAGE_HEIGHT = defaultPageSize[1]
    PAGE_WIDTH = defaultPageSize[0]

    def set_options(self, slug=None, round_id=None, session_id=None):
        if round_id:
            self.session_round = get_object_or_404(SessionRound, pk=round_id)
        else:
            self.session_round = None
        if session_id:
            self.session = get_object_or_404(Session, pk=session_id)
        else:
            self.session = None

    def get(self, request, **kwargs):
        self.set_options(**kwargs)
        self.update_style()
        elements = self.get_elements()
        return self.response(elements)

    def update_style(self):
        """Subclasses can customise to amend self.style"""
        pass

    def setMargins(self, doc):
        pass

    def get_filename(self):
        return self.filename or 'Download'

    def response(self, elements):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="%s %s.pdf"' % (self.competition, self.get_filename())
        doc = self.get_doc(response)
        self.setMargins(doc)
        doc.build(elements)
        return response

    def get_doc(self, response):
        doc = SimpleDocTemplate(response, pagesize=(self.PAGE_WIDTH, self.PAGE_HEIGHT))
        return doc

    def Para(self, string, style='Normal'):
        return Paragraph(str(string), self.styles[style])

    def get_elements(self):
        return [self.Para('This is not done yet')]


class HeadedPdfView(PdfView):
    title = ''
    title_position = 70
    do_sponsors = True

    def draw_title(self, canvas, doc, invert_dimensions=False):
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 18)
        if self.title:
            title = u'{0}: {1}'.format(self.competition, self.title)
        else:
            title = str(self.competition)
        width = self.PAGE_WIDTH
        height = self.PAGE_HEIGHT
        if invert_dimensions:
            width = self.PAGE_HEIGHT
            height = self.PAGE_WIDTH
        canvas.drawCentredString(width / 2.0, height - self.title_position, title)

        if self.do_sponsors:
            sponsors = self.competition.sponsors.all()

            positions = (
                (50, 20),
            )
            for i, sponsor in enumerate(sponsors):
                canvas.drawImage(
                    sponsors[i].logo.path,
                    positions[i][0],
                    positions[i][1],
                    width=self.PAGE_WIDTH - 100,
                    preserveAspectRatio=True,
                    anchor='nw',
                )

        canvas.restoreState()

    def get_filename(self):
        if self.filename:
            return self.filename
        if self.title:
            return self.title
        return super().get_filename()

    def response(self, elements):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="%s %s.pdf"' % (self.competition, self.get_filename())
        doc = self.get_doc(response)
        self.setMargins(doc)
        doc.build(elements, onFirstPage=self.draw_title, onLaterPages=self.draw_title)
        return response


class TargetListPdf(CompetitionMixin, HeadedPdfView):
    title = 'Target List'
    lunch = False
    admin_required = False

    def setMargins(self, doc):
        doc.topMargin = 1 * inch
        if self.competition.sponsors.exists():
            doc.bottomMargin = 1.5 * inch
        else:
            doc.bottomMargin = 0.5 * inch

    def update_style(self):
        self.styles['h2'].alignment = 1

    def get_elements(self):
        session_rounds = SessionRound.objects.filter(
            session__competition=self.competition,
        ).order_by('session__start').select_related('session')

        elements = []
        by_session = self.request.GET.get('by_session', False)
        if by_session:
            rounds_by_session = {r.session: r for r in session_rounds}
            session_rounds = rounds_by_session.values()
        for session_round in session_rounds:
            target_list = session_round.target_list_pdf(lunch=self.lunch, whole_session=by_session)
            if not target_list:
                continue

            if by_session:
                title = "Target List - {0}".format(session_round.session.start.strftime('%A, %d %B %Y, %X'))
            else:
                title = "Target List for {0} - {1}".format(
                    session_round.shot_round,
                    session_round.session.start.strftime('%A, %d %B %Y, %X'),
                )
            header = self.Para(title, 'h2')
            elements.append(header)
            table = Table(target_list)
            spacer = Spacer(self.PAGE_WIDTH, 0.25 * inch)

            elements += [spacer, table, spacer, PageBreak()]
        return elements


class TargetListLunch(TargetListPdf):
    lunch = True


class ScoreSheetsPdf(CompetitionMixin, HeadedPdfView):
    box_size = 0.32 * inch
    wide_box = box_size * 1.35
    total_cols = 1 + 12 + 2 + 4
    col_widths = 7 * [box_size] + [wide_box] + 6 * [box_size] + 6 * [wide_box]

    def get_filename(self):
        return 'Score Sheets - %s' % self.session_round.shot_round

    def setMargins(self, doc):
        doc.topMargin = 0.9 * inch

    def update_style(self):
        self.title = self.session_round.shot_round
        self.spacer = Spacer(self.PAGE_WIDTH, self.box_size * 0.5)

    def get_elements(self):
        score_sheet_elements = self.get_score_sheet_elements(self.session_round)
        target_list = self.session_round.target_list()

        elements = []
        for boss, entries in itertools.groupby(target_list, lambda x: x[0][:-1]):
            entries = list(entries)
            if not any(e[1] for e in entries):
                continue
            for target, entry in entries:
                table_data = self.header_table_for_entry(target, entry)
                header_table = Table(table_data, [0.6 * inch, 2.5 * inch, 3.9 * inch])
                if self.competition.ifaa_rules:
                    header_table.setStyle(TableStyle([
                         ('SPAN', (1, 1), (2, 1)),
                    ]))
                elements.append(KeepTogether([self.spacer, header_table, self.spacer] + score_sheet_elements))
            elements.append(PageBreak())

        return elements

    def header_table_for_entry(self, target, entry):
        if entry:
            entry = entry.session_entry.competition_entry
            category = u'{1} {0}'.format(entry.get_gender_display(), entry.bowstyle)
            if self.competition.ifaa_rules:
                category = entry.get_ifaa_division_display() + ' ' + category
            if self.competition.has_juniors and entry.age == 'J':
                category = 'Junior ' + category
            header_elements = [
                [
                    self.Para(target, 'h2'),
                    self.Para(entry.archer, 'h2'),
                    self.Para(entry.team_name(short_form=False), 'h2'),
                ],
                [
                    None,
                    self.Para(category, 'h2'),
                    None,
                ],
            ]
            category_labels = []
            if self.competition.has_novices:
                category_labels.append(entry.get_novice_display())
            if self.competition.has_agb_age_groups and entry.agb_age:
                category_labels.append(entry.get_agb_age_display())
            if category_labels:
                header_elements[1][2] = self.Para(' '.join(category_labels), 'h2')
            return header_elements
        else:
            return [
                [self.Para(target, 'h2'), None, None],
                [],
            ]

    def get_score_sheet_elements(self, session_round):
        if session_round.shot_round.is_ifaa:
            return self.get_ifaa_score_sheet(session_round, flint_round=session_round.shot_round.flint_round)
        subrounds = session_round.shot_round.subrounds.order_by('-distance')
        score_sheet_elements = []

        for subround in subrounds:
            subround_title = self.Para(u'{0}{1}'.format(subround.distance, subround.unit), 'h3')
            dozens = int(subround.arrows / 12)
            extra = subround.arrows % 12
            total_rows = dozens + 2
            scoring_labels = ['ET', 'S'] + session_round.shot_round.score_sheet_headings + ['RT']
            if session_round.shot_round.scoring_type == 'I':
                self.total_cols -= 1
            table_data = [['J', subround_title] + [None] * 5 + ['ET'] + [None] * 6 + scoring_labels]
            table_data += [[None for i in range(self.total_cols)] for j in range(total_rows - 1)]
            scores_table_style = copy.deepcopy(self.scores_table_style)
            if extra == 6:
                total_rows += 1
                table_data += [[None for i in range(self.total_cols)]]
                scores_table_style._cmds.append(('INNERGRID', (0, -2), (7, -2), 0.25, colors.black))
                scores_table_style._cmds.append(('LINEABOVE', (0, -2), (7, -2), 0.25, colors.black))
                scores_table_style._cmds[3][2] = (-1, -3)
                scores_table_style._cmds[4][2] = (-1, -3)
                scores_table_style._cmds[8][2] = (-1, -3)

            table = Table(table_data, self.col_widths, total_rows * [self.box_size])
            table.setStyle(scores_table_style)

            score_sheet_elements += [table, self.spacer]

        compound_round = bool(subrounds.count() - 1)
        if compound_round:
            totals_table = Table([[None] * self.total_cols], self.col_widths, [self.box_size])
            totals_table.setStyle(self.totals_table_style)

            score_sheet_elements += [totals_table, self.spacer]

        return score_sheet_elements + self.get_signing_footer()

    def get_signing_footer(self):
        signing_table_widths = [0.8 * inch, 2 * inch]
        signing_table = Table(
            [[self.Para('Archer', 'h3'), None, None, self.Para('Scorer', 'h3'), '']],
            signing_table_widths + [0.5 * inch] + signing_table_widths
        )
        signing_table.setStyle(self.signing_table_style)
        return [self.spacer, signing_table]

    def get_ifaa_score_sheet(self, session_round, flint_round=False):
        row_1 = [
            'Unit 1',
            None,
            None,
            None,
            None,
            'ET',
            'RT',
            None,
            'Unit 2',
            None,
            None,
            None,
            None,
            'ET',
            'RT',
        ]
        pen_row = [None] * 3 + ['Total Unit 1'] + [None] * 7 + ['Total Unit 2']
        end_row = [None] * 11 + ['Unit 1 + Unit 2']
        rows = 7 if flint_round else 6
        table_data = [row_1] + [[None for i in range(15)] for j in range(rows)] + [pen_row, end_row]

        if flint_round:
            table_data[1][0] = table_data[1][8] = '25Y'
            table_data[2][0] = table_data[2][8] = '20ft'
            table_data[3][0] = table_data[3][8] = '30Y'
            table_data[4][0] = table_data[4][8] = '15Y'
            table_data[5][0] = table_data[5][8] = '20Y'
            table_data[6][0] = table_data[6][8] = '10Y'
            table_data[7][0] = table_data[7][8] = 'W Up'

        box_size = self.box_size * 1.3
        col_widths = [
            box_size * (1.35 if flint_round else 1),
            box_size,
            box_size,
            box_size,
            box_size,
            box_size * 1.35,
            box_size * 1.35,
            box_size * 1.5,
            box_size * (1.35 if flint_round else 1),
            box_size,
            box_size,
            box_size,
            box_size,
            box_size * 1.35,
            box_size * 1.35,
        ]
        row_heights = (3 + rows) * [box_size / 1.4]

        table = Table(table_data, col_widths, row_heights)

        styles = [
            # alignment
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            # unit 1 grid
            ('BOX', (0, 1), (6, -3), 2, colors.black),
            ('INNERGRID', (0, 1), (6, -3), 0.25, colors.black),

            # unit 2 grid
            ('BOX', (8, 1), (-1, -3), 2, colors.black),
            ('INNERGRID', (8, 1), (-1, -3), 0.25, colors.black),

            # end totals columns
            ('BOX', (5, 0), (6, -2), 2, colors.black),
            ('INNERGRID', (5, 0), (6, -2), 0.25, colors.black),
            ('BOX', (-2, 0), (-1, -1), 2, colors.black),
            ('INNERGRID', (-2, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (-2, -1), (-1, -1), 2, colors.black),
        ]
        if flint_round:
            styles += [
                ('BOX', (0, 1), (0, -3), 2, colors.black),
                ('BOX', (8, 1), (8, -3), 2, colors.black),
            ]

        table.setStyle(TableStyle(styles))
        return [table, self.spacer] + self.get_signing_footer()

    scores_table_style = TableStyle([
        # alignment
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # arrows grid
        ('BOX', (1, 1), (7, -2), 2, colors.black),
        ['BOX', (8, 1), (-1, -2), 2, colors.black],
        ['INNERGRID', (0, 1), (-1, -2), 0.25, colors.black],

        # judges column
        ['BOX', (0, 1), (0, -2), 0.25, colors.black],
        ['BACKGROUND', (0, 1), (0, -2), colors.lightgrey],

        # end totals columns
        ('BOX', (7, 0), (7, -2), 2, colors.black),
        ['BOX', (14, 0), (14, -2), 2, colors.black],

        # totals grid
        ('BOX', (15, 0), (-1, -2), 2, colors.black),
        ('BOX', (15, -1), (-2, -1), 2, colors.black),
        ('LINEBEFORE', (16, 0), (-1, -1), 1.5, colors.black),

        # span for distance
        ('SPAN', (1, 0), (6, 0)),
    ])

    totals_table_style = TableStyle([
        ('BOX', (15, 0), (-2, 0), 2, colors.black),
        ('LINEBEFORE', (16, 0), (-1, -1), 1.5, colors.black),
    ])

    signing_table_style = TableStyle([
        ('LINEBELOW', (1, 0), (1, 0), 1, colors.black),
        ('LINEBELOW', (4, 0), (4, 0), 1, colors.black),
    ])


class SessionScoreSheetsPdf(ScoreSheetsPdf):
    def get_filename(self):
        return 'Score Sheets'

    def update_style(self):
        self.title = None
        self.spacer = Spacer(self.PAGE_WIDTH, self.box_size * 0.5)
        self.styles['h1'].alignment = 1

    def get_elements(self):
        session_rounds = self.session.sessionround_set.all()
        templates = {sr.shot_round: self.get_score_sheet_elements(sr) for sr in session_rounds}

        target_list = self.session.target_list()

        elements = []
        current_target = 0
        current_target_elements = []
        current_shot_round = None

        for target, entry in target_list:
            if not entry and not current_shot_round:
                continue
            target_number = re.match(r'\d+', target).group(0)
            if target_number != current_target:
                current_target = target_number
                elements.append(KeepTogether(current_target_elements))
                current_target_elements = []
            if entry:
                shot_round = entry.session_entry.session_round.shot_round
                if shot_round != current_shot_round:
                    current_shot_round = shot_round
            else:
                shot_round = current_shot_round
            table_data = self.header_table_for_entry(target, entry)
            header_table = Table(table_data, [0.6 * inch, 2.5 * inch, 4 * inch])
            sheet_elements = [
                self.spacer,
                self.Para(shot_round, 'h1'),
                self.spacer,
                header_table,
                self.spacer,
            ] + templates[shot_round]
            current_target_elements.append(KeepTogether(sheet_elements))
        elements.append(PageBreak())

        return elements


class RunningSlipsPdf(ScoreSheetsPdf):

    def get_filename(self):
        return 'Running Slips - %s' % self.session_round.shot_round

    def draw_title(self, canvas, doc):
        pass

    def setMargins(self, doc):
        doc.topMargin = doc.bottomMargin = 0.3 * inch

    def get_elements(self):
        elements = []
        targets = self.request.GET.get('targets', None)
        scoring_type = self.session_round.session.scoring_system
        archers_per_target = self.session_round.session.archers_per_target
        if targets is not None:
            targets = range(1, int(targets) + 1)
            details = 'ABCDEFG'
            boss_labels = [['%d%s' % (i, details[j]) for j in range(archers_per_target)] for i in targets]
            if scoring_type == SCORING_FULL:
                elements += self.get_full_running_slip_elements(boss_labels)
            elif scoring_type == SCORING_DOZENS:
                elements += self.get_dozen_running_slip_elements(boss_labels)
        else:
            all_entries = []
            for boss, entries in itertools.groupby(self.session_round.target_list(), lambda x: x[0][:-1]):
                entries = list(entries)
                if not functools.reduce(lambda e, f: e or f, [entry[1] for entry in entries]):
                    continue
                all_entries.append(entries)
            if scoring_type == SCORING_FULL:
                elements += self.get_full_running_slip_elements(all_entries)
            elif scoring_type == SCORING_DOZENS:
                elements += self.get_dozen_running_slip_elements(all_entries)
        return elements

    def get_full_running_slip_elements(self, all_entries):
        dozens = self.session_round.shot_round.arrows / 12
        elements = []
        headings = self.session_round.shot_round.score_sheet_headings
        if self.session_round.shot_round.scoring_type == 'I':
            self.total_cols -= 1
        while all_entries:
            entries_group, all_entries = all_entries[:6], all_entries[6:]
            for dozen in range(1, int(dozens) + 1):
                for entries in entries_group:
                    table_data = [(
                        ['Dozen {0}'.format(dozen)] + [None] * 6 + ['ET'] + [None] * 6 + ['ET', 'S'] + headings + ['RT' if dozen > 1 else 'Inits.']
                    )]
                    for entry in entries:
                        table_data.append([entry[0]] + [None for i in range(self.total_cols - 1)])
                    table = Table(table_data,
                        [self.box_size] + self.col_widths[1:], (len(entries) + 1) * [self.box_size])
                    table.setStyle(self.scores_table_style)
                    elements.append(KeepTogether(table))
                    elements += [self.spacer]
        return elements

    def get_dozen_running_slip_elements(self, all_entries):
        dozens = self.session_round.shot_round.arrows / 12
        elements = []
        while all_entries:
            entries_group, all_entries = all_entries[:6], all_entries[6:]
            for dozen in range(1, int(dozens)):
                for entries in entries_group:
                    # we don't do the last dozen here
                    table_data = [
                        ['Dozen {0}'.format(dozen)] + [entry[0] for entry in entries],
                        ['Score'] + [None for e in entries],
                        ['Running Total' if dozen > 1 else 'Initials'] + [None for e in entries],
                    ]
                    table = Table(table_data, [self.box_size * 4] * 5, [self.box_size * 1.5] * 3)
                    table.setStyle(self.dozens_table_style)
                    elements.append(KeepTogether(table))
                    elements += [self.spacer] * 2
                elements.append(PageBreak())
        return elements

    scores_table_style = TableStyle([
        # alignment
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # arrows grid
        ('BOX', (0, 1), (-1, -1), 2, colors.black),
        ('INNERGRID', (0, 1), (-1, -1), 0.25, colors.black),

        # end totals columns
        ('BOX', (7, 0), (7, -1), 2, colors.black),
        ('BOX', (14, 0), (14, -1), 2, colors.black),

        # details column
        ('BOX', (0, 1), (0, -1), 2, colors.black),

        # totals grid
        ('BOX', (15, 0), (-1, -1), 2, colors.black),
        ('LINEBEFORE', (15, 0), (-1, -1), 1.5, colors.black),

        # title
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
    ])

    dozens_table_style = TableStyle([
        # alignment
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # grid
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
    ])

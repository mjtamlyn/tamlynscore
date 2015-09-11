import copy

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView

from entries.models import CompetitionEntry
from scoring.utils import class_view_decorator
from scores.models import Score

from .models import County, Club, Archer
from .forms import ArcherForm


class ClubMixin(object):
    def dispatch(self, request, *args, **kwargs):
        self.club = get_object_or_404(Club, slug=self.kwargs['club_slug'])
        return super().dispatch(request, *args, **kwargs)

    def get_archer_queryset(self):
        entries = Prefetch(
            'competitionentry_set',
            queryset=CompetitionEntry.objects.select_related('competition', 'competition__tournament'),
            to_attr='entries',
        )
        return self.club.archer_set.select_related('bowstyle').order_by('name').prefetch_related(entries)

    def get_context_data(self, **kwargs):
        return super().get_context_data(club=self.club, **kwargs)


@class_view_decorator(login_required)
class Index(TemplateView):
    template_name = 'index.html'


@class_view_decorator(login_required)
class ClubList(ListView):
    model = Club


@class_view_decorator(login_required)
class ClubDetail(ClubMixin, TemplateView):
    template_name = 'core/club_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ClubDetail, self).get_context_data(**kwargs)
        context['archers'] = self.get_archer_queryset().filter(
            archived=False,
        )
        context['archived_archer_count'] = self.club.archer_set.filter(
            archived=True,
        ).count()
        return context


@class_view_decorator(login_required)
class ClubUpdate(ClubMixin, UpdateView):
    fields = '__all__'

    def get_object(self):
        return self.club


@class_view_decorator(login_required)
class ArchiveArcherList(ClubMixin, ListView):
    template_name = 'core/archive_archers.html'
    context_object_name = 'archers'

    def get_queryset(self):
        return self.get_archer_queryset().filter(archived=True)


@class_view_decorator(login_required)
class ClubCreate(CreateView):
    model = Club
    fields = '__all__'

    def get_success_url(self):
        return self.request.GET.get('next') or super(ClubCreate, self).get_success_url()


@class_view_decorator(login_required)
class CountyCreate(CreateView):
    model = County
    fields = '__all__'

    def get_success_url(self):
        return self.request.GET.get('next') or reverse('home')


@class_view_decorator(login_required)
class ArcherDetail(DetailView):
    model = Archer

    def get_context_data(self, **kwargs):
        entries = self.object.competitionentry_set.order_by('-competition__date')
        shoots = []
        for entry in entries:
            scores = Score.objects.filter(target__session_entry__competition_entry=entry)
            shoots.append({
                'competition': entry.competition,
                'bowstyle': entry.bowstyle,
                'scores': [{
                    'round': s.target.session_entry.session_round.shot_round,
                    'score': s.score,
                } for s in scores],
            })
        return super(ArcherDetail, self).get_context_data(shoots=shoots, **kwargs)


@class_view_decorator(login_required)
class ArcherUpdate(UpdateView):
    model = Archer
    form_class = ArcherForm

    def get_success_url(self):
        return self.request.GET.get('next') or self.request.path


@class_view_decorator(login_required)
class ArcherCreate(CreateView):
    model = Archer
    form_class = ArcherForm

    def get_initial(self):
        initial = {}
        cached = cache.get('archer-create-%s' % self.request.user.pk)
        if cached:
            initial = cached
        name = self.request.GET.get('name')
        if name:
            initial['name'] = name
        return initial

    def form_valid(self, form):
        cache_data = copy.copy(form.cleaned_data)
        del cache_data['name']
        cache.set('archer-create-%s' % self.request.user.pk, cache_data)
        return super(ArcherCreate, self).form_valid(form)

    def get_success_url(self):
        competition = self.request.GET.get('competition')
        if competition:
            return reverse('entry_add', kwargs={
                'slug': competition,
                'archer_id': self.object.pk,
            })
        return self.object.club.get_absolute_url()


@class_view_decorator(login_required)
class ArcherArchive(UpdateView):
    model = Archer
    fields = ['archived']

    def get_success_url(self):
        return self.object.club.get_absolute_url()

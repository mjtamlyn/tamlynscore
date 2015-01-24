from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, CreateView

from scoring.utils import class_view_decorator
from scores.models import Score

from .models import Club, Archer


@class_view_decorator(login_required)
class Index(TemplateView):
    template_name = 'index.html'


@class_view_decorator(login_required)
class ClubList(ListView):
    model = Club


@class_view_decorator(login_required)
class ClubDetail(DetailView):
    model = Club

    def get_context_data(self, **kwargs):
        archers = self.object.archer_set.order_by('name')
        return super(ClubDetail, self).get_context_data(archers=archers, **kwargs)


@class_view_decorator(login_required)
class ClubUpdate(UpdateView):
    model = Club


@class_view_decorator(login_required)
class ClubCreate(CreateView):
    model = Club

    def get_success_url(self):
        return self.request.GET.get('next') or super(ClubCreate, self).get_success_url()


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

    def get_success_url(self):
        return self.request.GET.get('next') or self.request.path

from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, DetailView, UpdateView

from scoring.utils import class_view_decorator

from .forms import ArcherUpdateForm
from .models import Club, Archer


@class_view_decorator(login_required)
class Index(TemplateView):
    template_name = 'index.html'


class ClubList(ListView):
    model = Club


class ClubDetail(DetailView):
    model = Club


@class_view_decorator(login_required)
class ArcherUpdate(UpdateView):
    model = Archer
    form_class = ArcherUpdateForm

    def get_success_url(self):
        return self.request.GET.get('next') or self.request.path
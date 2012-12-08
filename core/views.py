from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, DetailView, UpdateView

from .forms import ArcherUpdateForm
from .models import Club, Archer

from scoring.utils import class_view_decorator

@class_view_decorator(login_required)
class Index(TemplateView):
    template_name = 'index.html'

class ClubList(ListView):
    model = Club
club_list = login_required(ClubList.as_view())

class ClubDetail(DetailView):
    model = Club
club_detail = login_required(ClubDetail.as_view())


class ArcherUpdate(UpdateView):
    model = Archer
    form_class = ArcherUpdateForm

    def get_success_url(self):
        return self.request.GET.get('next') or self.request.path

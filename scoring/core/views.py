from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, DetailView

from core.models import Club

class Index(TemplateView):
    template_name = 'index.html'
index = login_required(Index.as_view())

class ClubList(ListView):
    model = Club
club_list = login_required(ClubList.as_view())

class ClubDetail(DetailView):
    model = Club
club_detail = login_required(ClubDetail.as_view())


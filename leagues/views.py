from django.views.generic import DetailView, ListView

from .models import League


class LeagueList(ListView):
    model = League


class LeagueDetail(DetailView):
    model = League
    slug_url_kwarg = 'league_slug'

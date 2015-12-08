from django.views.generic import DetailView, ListView

from .models import League, Season


class LeagueList(ListView):
    model = League


class LeagueDetail(DetailView):
    model = League
    slug_url_kwarg = 'league_slug'


class SeasonDetail(DetailView):
    slug_url_kwarg = 'season_slug'

    def get_queryset(self):
        return Season.objects.filter(league__slug=self.kwargs['league_slug'])

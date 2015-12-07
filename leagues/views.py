from django.views.generic import ListView

from .models import League


class LeagueList(ListView):
    model = League

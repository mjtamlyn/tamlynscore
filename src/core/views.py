from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import View

from core.models import Club

@login_required
def index(request):
    return render(request, 'index.html', locals())

class ClubView(View):
    def get(self, request):
        clubs = Club.objects.all()
        return render(request, 'clubs.html', locals())
clubs = login_required(ClubView.as_view())

@login_required
def club_index(request, club):
    club = Club.objects.get(slug=club)
    return render(request, 'club_index.html', locals())


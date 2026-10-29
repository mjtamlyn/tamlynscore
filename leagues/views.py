from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from braces.views import MessageMixin

from scores.models import Score
from scores.result_modes import get_mode

from .forms import LegCreateForm
from .models import League, Leg, ResultsMode, Season


class LeagueMixin(MessageMixin):
    organiser_required = True

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.league = get_object_or_404(League, slug=kwargs['league_slug'])
        self.is_organiser = self.request.user.is_superuser or self.request.user in self.league.organisers.all()

    def check_permission(self):
        return self.is_organiser or not self.organiser_required

    def dispatch(self, request, *args, **kwargs):
        if not self.check_permission():
            self.messages.error('You must be logged in as a league organiser to do that.')
            return HttpResponseRedirect(reverse('league-detail', kwargs={'leage_slug': self.kwargs['league_slug']}))
        return super().dispatch(request, *args, **kwargs)

    def get_meta_description(self):
        return '{}, hosted on TamlynScore.'.format(self.league)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'league': self.league,
            'is_organiser': self.is_organiser,
            'title': str(self.league),
            'meta_description': self.get_meta_description(),
        })
        return context


#######################
# PUBLIC LEAGUE PAGES #
#######################

class LeagueList(ListView):
    model = League


class LeagueDetail(LeagueMixin, DetailView):
    model = League
    organiser_required = False

    def get_object(self):
        return self.league


class SeasonDetail(LeagueMixin, DetailView):
    slug_url_kwarg = 'season_slug'
    organiser_required = False

    def get_queryset(self):
        return Season.objects.filter(league=self.league)

    def get_context_data(self, **kwargs):
        context = super(SeasonDetail, self).get_context_data(**kwargs)
        context['legs'] = self.object.leg_set.order_by('name')
        context['editions'] = self.league.season_set.order_by('-start_date').exclude(pk=self.object.pk)
        context['non_leg_competitions'] = self.object.non_leg_competitions.order_by('date')
        return context


class Results(TemplateView):
    template_name = 'leagues/leg_results.html'

    def get(self, request, *args, **kwargs):
        self.leg = self.get_leg()
        self.format = self.get_format()
        self.mode = self.get_mode()
        self.object_list = self.get_scores()
        context = self.get_context_data(object_list=self.object_list)
        return self.render_to_response(context)

    def get_format(self):
        format = self.kwargs['format']
        if format not in ['html', 'pdf', 'pdf-summary', 'big-screen', 'csv', 'json']:
            raise Http404('No such format')
        return format

    def get_leg(self):
        return get_object_or_404(
            Leg,
            slug=self.kwargs['leg_slug'],
            season__slug=self.kwargs['season_slug'],
            season__league__slug=self.kwargs['league_slug'],
        )

    def get_scores(self):
        scores = Score.objects.filter(
            target__session_entry__competition_entry__competition__in=self.leg.competitions.all()
        ).select_related(
            'target',
            'target__session_entry',
            'target__session_entry__session_round',
            'target__session_entry__session_round__shot_round',
            'target__session_entry__competition_entry',
            'target__session_entry__competition_entry__competition',
            'target__session_entry__competition_entry__archer',
            'target__session_entry__competition_entry__bowstyle',
            'target__session_entry__competition_entry__club',
        ).order_by(
            '-target__session_entry__competition_entry__age',
            '-target__session_entry__competition_entry__agb_age',
            'target__session_entry__competition_entry__novice',
            'target__session_entry__competition_entry__bowstyle',
            'target__session_entry__competition_entry__archer__gender',
        )
        return scores

    def get_mode(self, load=False):
        mode = get_mode(self.kwargs['mode'], include_distance_breakdown=False, hide_golds=False)
        if not mode:
            raise Http404('No such mode')
        if load:
            exists, obj = self.mode_exists(mode, load=True)
        else:
            exists = self.mode_exists(mode)
        if not exists:
            raise Http404('No such mode for this competition')
        return (mode, obj) if load else mode

    def mode_exists(self, mode, load=False):
        if load:
            try:
                obj = self.leg.result_modes.filter(mode=mode.slug).get()
            except ResultsMode.DoesNotExist:
                return False, None
            else:
                return True, obj
        else:
            return self.leg.result_modes.filter(mode=mode.slug).exists()

    def get_context_data(self, **kwargs):
        kwargs['results'] = self.mode.get_results(self.leg, kwargs['object_list'], leaderboard=False, request=self.request)
        kwargs['mode'] = self.mode
        kwargs['leg'] = self.leg
        return super().get_context_data(**kwargs)

    def render_to_response(self, context, **response_kwargs):
        results = context['results']
        if self.format == 'pdf':
            return self.render_to_pdf(context)
        elif self.format == 'pdf-summary':
            context['results'] = self.cut_results(results)
            return self.render_to_pdf(context)
        elif self.format == 'csv':
            return self.render_to_csv(context)
        elif self.format == 'json':
            return self.render_to_json(context)
        for section in results:
            for category in results[section]:
                for score in results[section][category]:
                    score.details = self.mode.score_details(score, section)
                    if getattr(score, 'team', None):
                        for archer in score.team:
                            archer.details = self.mode.score_details(archer, section)
        return super().render_to_response(context, **response_kwargs)


##########################
# LEAGUE ORGANISER TOOLS #
##########################

class LegCreateView(LeagueMixin, CreateView):
    model = Leg
    form_class = LegCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['league'] = self.league
        # TODO: SeasonQuerySet.filter_current()
        self.season = kwargs['season'] = self.league.season_set.order_by('-start_date').first()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['season'] = self.season
        return context

    def get_success_url(self):
        return self.season.get_absolute_url()

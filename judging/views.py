from django.contrib.auth import login
from django.http import Http404
from django.urls import reverse
from django.views.generic import RedirectView, TemplateView

from braces.views import MessageMixin

from entries.models import SessionEntry
from entries.views import CompetitionMixin, Registration
from olympic.match_loader import MatchLoader

from .models import Judge


class JudgeMixin(CompetitionMixin):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            judge_user = self.competition.judge
        except Judge.DoesNotExist:
            judge_user = Judge.objects.create(competition=self.competition)
        self.user_is_judge = self.request.user == judge_user
        self.judge_user = judge_user

    def check_permission(self):
        return self.user_is_judge or self.is_admin

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            user_is_judge=self.user_is_judge,
            judge_user=self.judge_user,
            judge_login_url=self.request.build_absolute_uri(
                reverse('judge_authenticate', kwargs={'id': self.judge_user.uuid})
            ),
            **kwargs
        )


class JudgeIndex(JudgeMixin, TemplateView):
    template_name = 'judging/index.html'


class JudgeInspection(JudgeMixin, Registration):
    template_name = 'judging/inspection.html'

    def post(self, request, slug):
        inspected = request.POST['kit_inspected'] == 'true'
        updated = SessionEntry.objects.filter(pk=request.POST['pk']).update(kit_inspected=inspected)
        if not updated:
            raise Http404
        return self.get(request, slug)


class JudgeMatches(JudgeMixin, TemplateView):
    template_name = 'judging/matches.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        matches = MatchLoader(self.competition)
        matches.load_all()
        context['matches_by_time'] = matches.matches_by_time()

        return context


class JudgeAuthenticate(MessageMixin, RedirectView):
    permanent = False

    def dispatch(self, request, *args, **kwargs):
        self.judge_user = Judge.objects.get(uuid=kwargs['id'])
        if self.judge_user.competition.is_admin(request.user):
            self.messages.error('You are logged in already as a competition admin - you must log out before you can log in as a judge.')
        else:
            login(request, self.judge_user, backend='judging.auth_backends.JudgeAuthBackend')
        return super().dispatch(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse('judge_index', kwargs={'slug': self.judge_user.competition.slug})

from django.contrib.auth import login
from django.http import Http404
from django.urls import reverse
from django.views.generic import RedirectView, TemplateView

from braces.views import MessageMixin

from entries.models import SessionEntry
from entries.views import CompetitionMixin, Registration
from olympic.models import Seeding
from olympic.views import FieldPlanMixin

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


class JudgeMatches(FieldPlanMixin, JudgeMixin, TemplateView):
    template_name = 'judging/matches.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        matches = self.get_matches().prefetch_related('session_round__category__bowstyles')
        if len(matches) == 0:
            return context

        session_rounds = {m.session_round for m in matches}
        seedings = Seeding.objects.filter(session_round__in=session_rounds)
        seedings_dict = {(s.session_round_id, s.seed): s for s in seedings}

        max_levels = {session_round: max(m.level for m in matches if m.session_round == session_round) for session_round in session_rounds}

        max_timing = (max(matches, key=lambda m: m.timing)).timing
        last_match = max(matches, key=lambda m: (m.target_2 or m.target))
        max_target = last_match.target_2 or last_match.target
        if matches[0].session_round.shot_round.team_type:
            max_target += 1
        levels = ['Final', 'Semis', 'Quarters', '1/8', '1/16', '1/32', '1/64', '1/128']
        passes = 'ABCDEFGHIJK'

        layout = [{
            'name': 'Pass %s' % letter,
            'targets': [{
                'number': i,
                'match': None,
                'category': None,
                'round': None,
                'is_bye': False,
                'has_second_target': False,
                'is_second_target': False,
                'archer_1': None,
                'archer_2': None,
                'seed_1': None,
                'seed_2': None,
            } for i in range(1, max_target + 1)],
        } for letter in passes[:max_timing]]
        for m in matches:
            slot = layout[m.timing - 1]['targets'][m.target - 1]
            slot['match'] = m
            slot['category'] = m.session_round.category.name
            slot['distance'] = '%sm' % m.session_round.shot_round.distance
            slot['round'] = levels[m.level - 1]
            if m.level == 1 and m.match == 2:
                slot['round'] = 'Bronze'
            seeds = [m.match, (2 ** m.level) + 1 - m.match]
            if not m.match % 2:
                seeds.reverse()
            if m.level == max_levels[m.session_round] and seedings_dict:
                seed_1 = seedings_dict.get((m.session_round_id, seeds[0]), None)
                if seed_1:
                    slot['seed_1'] = seed_1.seed
                    slot['archer_1'] = seed_1.entry.archer
                else:
                    slot['archer_1'] = 'BYE'
                seed_2 = seedings_dict.get((m.session_round_id, seeds[1]), None)
                if seed_2:
                    slot['seed_2'] = seed_2.seed
                    slot['archer_2'] = seed_2.entry.archer
                else:
                    slot['archer_2'] = 'BYE'
                if not seed_1 or not seed_2:
                    slot['is_bye'] = True
            else:
                slot['seed_1'] = seeds[0]
                slot['archer_1'] = 'TBC'
                slot['seed_2'] = seeds[1]
                slot['archer_2'] = 'TBC'

            if m.target_2:
                slot_2 = layout[m.timing - 1]['targets'][m.target_2 - 1]
                slot_2['match'] = slot['match']
                slot_2['category'] = slot['category']
                slot_2['distance'] = slot['distance']
                slot_2['round'] = slot['round']
                slot['has_second_target'] = True
                slot_2['is_second_target'] = True

                if (not slot['is_bye']) and slot['seed_1'] and slot['seed_2']:
                    slot_2['archer_1'] = slot['archer_2']
                    slot_2['seed_1'] = slot['seed_2']

        context['layout'] = layout

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

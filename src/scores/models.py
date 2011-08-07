from django.db import models

from entries.models import TargetAllocation

from itertools import groupby

class ScoreManager(models.Manager):
    def active(self, session_round, category=None):
        active_targets = TargetAllocation.objects.filter(session_entry__session_round=session_round).filter(session_entry__present=True)
        active_scores = self.filter(target__in=active_targets).select_related()
        targets_with_scores = [score.target for score in active_scores]
        for target in active_targets:
            if target not in targets_with_scores:
                score = Score(target=target)
                score.save()
        active_scores = self.filter(target__in=active_targets).select_related().order_by('target__boss')
        if category:
            active_scores = active_scores.filter(target__session_entry__competition_entry__bowstyle__in=category.bowstyles.all(), target__session_entry__competition_entry__archer__gender=category.gender)
        return active_scores

    def results(self, session_round, leaderboard=True, category=None):
        print session_round
        scores = self.active(session_round, category=category)
        if not leaderboard:
            scores = scores.annotate(arrows=models.Count('arrow')).filter(arrows__ne=session_round.shot_round.arrows)
        # TODO: Don't do this here!
        for score in scores:
            score.update_score()
            score.save()
        scores = scores.order_by(
                'target__session_entry__competition_entry__bowstyle',
                'target__session_entry__competition_entry__archer__gender',
                '-score', 
                '-golds', 
                '-xs'
                )
        if category:
            results = scores
        else:
            results = []
            for category, scores in groupby(scores, lambda s: s.target.session_entry.competition_entry.category()):
                results.append((category, list(scores)))
        return results

    def boss_groups(self, session_round):
        active = self.active(session_round)
        bosses = []
        for boss, entries in groupby(active, lambda s: s.target.boss):
            bosses.append((boss, list(entries)))
        return bosses

class Score(models.Model):
    target = models.ForeignKey(TargetAllocation)

    score = models.PositiveIntegerField(default=0, db_index=True)
    hits = models.PositiveIntegerField(default=0)
    golds = models.PositiveIntegerField(default=0)
    xs = models.PositiveIntegerField(default=0)

    retired = models.BooleanField(default=False)

    objects = ScoreManager()

    def __unicode__(self):
        return u'Score for {0}'.format(self.target)

    def update_score(self):
        self.score = self.arrow_set.aggregate(models.Sum('arrow_value'))['arrow_value__sum']
        self.hits = self.arrow_set.filter(arrow_value__gt=0).count()
        self.golds = self.arrow_set.filter(arrow_value=10).count()
        self.xs = self.arrow_set.filter(is_x=True).count()
        if not self.score:
            self.score = 0

    def running_total(self, dozen):
        return self.arrow_set.filter_up_to_dozen(dozen).aggregate(models.Sum('arrow_value'))['arrow_value__sum']

class ArrowManager(models.Manager):
    def filter_by_dozen(self, dozen):
        return self.filter(arrow_of_round__lte=(dozen+1)*12, arrow_of_round__gt=dozen*12)

    def filter_up_to_dozen(self, dozen):
        return self.filter(arrow_of_round__lte=int(dozen)*12)

class Arrow(models.Model):
    score = models.ForeignKey(Score)
    arrow_value = models.PositiveIntegerField()
    arrow_of_round = models.PositiveIntegerField()
    is_x = models.BooleanField(default=False)

    objects = ArrowManager()

    def __unicode__(self):
        if self.is_x:
            return u'X'
        if self.arrow_value == 0:
            return u'M'
        return unicode(self.arrow_value)


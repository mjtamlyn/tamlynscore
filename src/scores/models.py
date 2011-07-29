from django.db import models

from entries.models import TargetAllocation

from itertools import groupby

class ScoreManager(models.Manager):
    def active(self, session_round):
        active_targets = TargetAllocation.objects.filter(session_entry__session_round=session_round).filter(session_entry__present=True)
        active_scores = self.filter(target__in=active_targets).select_related()
        targets_with_scores = [score.target for score in active_scores]
        for target in active_targets:
            if target not in targets_with_scores:
                score = Score(target=target)
                score.save()
        active_scores = self.filter(target__in=active_targets).select_related().order_by('target__boss')
        return active_scores

    def results(self, session_round, leaderboard=True):
        scores = self.active(session_round)
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
        results = []
        for category, scores in groupby(scores, lambda s: s.target.session_entry.competition_entry.code()):
            results.append((category, list(scores)))
        return results

    def boss_groups(self, session_round):
        active = self.active(session_round)
        bosses = []
        for boss, entries in groupby(active, lambda s: s.target.boss):
            bosses.append(boss)
        return bosses

class Score(models.Model):
    target = models.ForeignKey(TargetAllocation)

    score = models.PositiveIntegerField(default=0)
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

class Arrow(models.Model):
    score = models.ForeignKey(Score)
    arrow_value = models.PositiveIntegerField()
    arrow_of_round = models.PositiveIntegerField()
    is_x = models.BooleanField(default=False)

    def __unicode__(self):
        if self.is_x:
            return u'X'
        if self.arrow_value == 0:
            return u'M'
        return unicode(self.arrow_value)


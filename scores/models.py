from django.db import models

from entries.models import TargetAllocation, SCORING_FULL, SCORING_DOZENS

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
        scores = self.active(session_round, category=category)
        scores = scores.select_related()
        if not leaderboard:
            scores = scores.annotate(arrows=models.Count('arrow')).filter(arrows__ne=session_round.shot_round.arrows)
        scores = scores.order_by(
                'target__session_entry__competition_entry__bowstyle',
                'target__session_entry__competition_entry__archer__gender',
                'disqualified',
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

    alteration = models.IntegerField(default=0)

    retired = models.BooleanField(default=False)
    disqualified = models.BooleanField(default=False)

    objects = ScoreManager()

    def __unicode__(self):
        return u'Score for {0}'.format(self.target)

    def update_score(self):
        if self.target.session_entry.session_round.session.scoring_system == SCORING_FULL:
            arrows = self.arrow_set.all()
            self.score = self.alteration
            self.hits = 0
            self.golds = 0
            self.xs = 0
            for arrow in arrows:
                self.score += arrow.arrow_value
                if arrow.arrow_value > 0:
                    self.hits += 1
                if arrow.arrow_value == 10:
                    self.golds += 1
                if arrow.is_x:
                    self.xs += 1
        elif self.target.session_entry.session_round.session.scoring_system == SCORING_DOZENS:
            self.score = self.dozen_set.aggregate(total=models.Sum('total'))['total'] or 0

    @property
    def arrows_entered_per_end(self):
        return self.target.session_entry.session_round.session.arrows_entered_per_end

    def running_total(self, dozen):
        if self.target.session_entry.session_round.session.scoring_system == SCORING_FULL:
            return self.arrow_set.filter(arrow_of_round__lte=int(dozen)*self.arrows_entered_per_end).aggregate(models.Sum('arrow_value'))['arrow_value__sum']
        elif self.target.session_entry.session_round.session.scoring_system == SCORING_DOZENS:
            return self.dozen_set.filter(dozen__lt=dozen).aggregate(total=models.Sum('total'))['total'] or 0


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


class Dozen(models.Model):
    score = models.ForeignKey(Score)
    total = models.PositiveIntegerField()
    dozen = models.PositiveIntegerField()

    def __unicode__(self):
        return self.total

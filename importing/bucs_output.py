import csv
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scoring.settings')  # NOQA


from entries.models import Competition, TargetAllocation

bucs = Competition.objects.filter(slug='bucs-indoors-2014')

entries = TargetAllocation.objects.filter(session_entry__competition_entry__competition=bucs).select_related()

writer = csv.writer(sys.stdout)
writer.writerow(['entry id', 'session time', 'target', 'name', 'bowstyle', 'gender', 'experience'])

for t in entries:
    se = t.session_entry
    ce = se.competition_entry
    s = se.session_round.session
    writer.writerow([
        ce.pk,
        s.start.hour,
        '%s%s' % (t.boss, t.target),
        ce.archer,
        ce.club.name,
        ce.bowstyle,
        ce.archer.get_gender_display(),
        ce.get_novice_display(),
    ])

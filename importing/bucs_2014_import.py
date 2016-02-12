import csv
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scoring.settings')  # NOQA


from entries.models import Competition, SessionRound, CompetitionEntry, SessionEntry, TargetAllocation


bucs = Competition.objects.filter(slug='bucs-indoors-2014')

SessionEntry.objects.filter(competition_entry__competition=bucs).delete()

sessions = SessionRound.objects.filter(session__competition=bucs).order_by('session__start')

session_key = dict(zip(['9am', '12pm', '3pm'], sessions))

reader = csv.reader(sys.stdin)

for row in reader:
    session, boss, target, cid, name, _, _, _, _, notes = row
    if notes or not cid:
        print(row)
        continue
    ce = CompetitionEntry.objects.get(id=cid)
    if not ce.archer.name == name:
        print('Bad name for archer %s (%s, %s%s)' % (name, session, boss, target))
    se = SessionEntry(
        competition_entry=ce,
        session_round=session_key[session],
    )
    se.save()
    ta = TargetAllocation(
        session_entry=se,
        boss=boss,
        target=target,
    )
    ta.save()

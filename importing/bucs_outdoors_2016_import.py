import csv
import os
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scoring.settings')  # NOQA

import django
django.setup()  # NOQA


from core.models import Archer, Bowstyle, Club
from entries.models import Competition, SessionRound, CompetitionEntry


bucs = Competition.objects.get(slug='bucs-outdoors-2016')

sessions = SessionRound.objects.filter(session__competition=bucs).order_by('session__start')


saturday_round_lookup = {
    'Saturday - BUCS Men\'s Experienced': 'WA 1440 (Gents)',
    'Saturday - BUCS Men\'s Novice': 'WA 1440 (Ladies)',
    'Saturday - BUCS Women\'s Experienced': 'WA 1440 (Ladies)',
    'Saturday - BUCS Women\'s Novice': 'Metric II',
}
for k, v in saturday_round_lookup.items():
    saturday_round_lookup[k] = sessions.get(shot_round__name__icontains=v)

sunday_round_lookup = {
    'Compound': sessions.get(shot_round__name__icontains='50'),
    'Recurve': sessions.get(shot_round__name__icontains='70'),
    'Barebow': sessions.get(shot_round__name__icontains='70'),
    'Longbow': sessions.get(shot_round__name__icontains='70'),
}

saturday = csv.DictReader(open('/Users/marc/Downloads/bucs-2016-saturday.csv'))
sunday = csv.DictReader(open('/Users/marc/Downloads/bucs-2016-sunday.csv'))

lookup_by_agb = defaultdict(list)
manual = []
new = []
fixable = []
success = {}

for row in saturday:
    lookup_by_agb[row['ArcheryGB']].append(row)


for row in sunday:
    lookup_by_agb[row['ArcheryGB']].append(row)


for number, rows in lookup_by_agb.items():
    try:
        number = int(number)
    except ValueError:
        manual.append(rows)
        continue
    if number == 0:
        manual.append(rows)
        continue
    given_name = '%s %s' % (rows[0]['FIRSTNAME'].strip(), rows[0]['LASTNAME'].strip())
    try:
        archer = Archer.objects.get(agb_number=number)
    except Archer.DoesNotExist:
        try:
            archer = Archer.objects.get(name=given_name)
        except Archer.DoesNotExist:
            new.append(rows)
        else:
            success[archer] = rows
    else:
        if not archer.name.lower() == given_name.lower():
            # print('MISMATCH', archer.name, given_name)
            success[archer] = rows
        else:
            success[archer] = rows

print('FIXABLE', len(fixable))
print('MANUAL', len(manual))
print('NEW', len(new))
print('SUCCESS!', len(success))


def extract_bowstyle_from_event(event):
    for b in Bowstyle.objects.all():
        if b.name in event:
            return b
    raise Exception('Cannot find bowstyle in %s' % event)


def extract_gender_from_event(event):
    if 'Men' in event or 'Male' in event:
        return 'G'
    if 'Women' in event or 'Female' in event:
        return 'L'
    raise Exception('Cannot find gender in %s' % event)


def extract_novice_from_event(event):
    if 'Novice' in event:
        return 'N'
    return 'E'


for archer, rows in success.items():
    details = []
    for row in rows:
        bowstyle = extract_bowstyle_from_event(row['EVENT'])
        gender = extract_gender_from_event(row['EVENT'])
        novice = extract_novice_from_event(row['EVENT'])
        uni = archer.club.short_name.replace('Uni', '').strip()
        if uni not in row['INSTITUTION']:
            club_name = row['INSTITUTION'].replace('University of ', '').replace(' University', '')
            try:
                uni = Club.objects.get(name__icontains=club_name)
            except Club.DoesNotExist:
                try:
                    uni = Club.objects.get(short_name__icontains=club_name + ' Uni')
                except Club.DoesNotExist:
                    print('FAIL!', club_name)
            except Club.MultipleObjectsReturned:
                try:
                    uni = Club.objects.get(short_name__icontains=club_name + ' Uni')
                except Club.DoesNotExist:
                    print('FAIL!', club_name)
        else:
            uni = archer.club
        shot_round = None
        for prefix, sr in saturday_round_lookup.items():
            if row['EVENT'].startswith(prefix):
                shot_round = sr
        if shot_round is None:
            assert 'No BUCS' in row['EVENT']
            shot_round = sunday_round_lookup[bowstyle.name]
        details.append((bowstyle, gender, uni, novice, shot_round))
    if any(deets[3] == 'N' for deets in details):
        novice = 'N'
    else:
        novice = 'E'
    bowstyle = details[0][0]
    gender = details[0][1]
    club = details[0][2]
    rounds = [deets[4] for deets in details]

    entry = CompetitionEntry.objects.create(
        competition=bucs,
        archer=archer,
        club=club,
        bowstyle=bowstyle,
        novice=novice,
    )
    for r in rounds:
        entry.sessionentry_set.create(session_round=r)

for archer in new:
    for row in archer:
        print(row['FIRSTNAME'], row['LASTNAME'], row['EVENT'], row['INSTITUTION'], row['ArcheryGB'])
for archer in manual:
    for row in archer:
        print(row['FIRSTNAME'], row['LASTNAME'], row['EVENT'], row['INSTITUTION'], row['ArcheryGB'])

import csv
from django.template.defaultfilters import slugify

from core.models import Bowstyle, Club, Archer
from entries.models import CompetitionEntry, SessionEntry, SessionRound, Competition, TargetAllocation

competition = Competition.objects.get(slug='bucs-indoors-2012')
session_rounds = SessionRound.objects.filter(session__competition=competition)

clubs = set()
total = 0
for session_name, session_round in zip(['A', 'B', 'C'], session_rounds):
    file_name = '/home/marc/Desktop/BUSA%s.csv' % session_name
    f = open(file_name, 'r')
    reader = csv.reader(f)
    rows = filter(lambda r: r[1], reader)
    rows = [row[:5] for row in rows]
    for target, archer, bow, club, exp in rows:
        bowstyle = Bowstyle.objects.get(name__iexact=bow)
        #if exp[0] not in ['E', 'N']:
        #    print exp
        exp = exp[0]
        club = Club.objects.get(short_name__iexact=club.strip() + ' Uni')
        # get or create archer
        try:
            archer = Archer.objects.get(name__iexact=archer, club=club)
        except Archer.DoesNotExist:
            archer = Archer(name=archer, club=club, novice=exp, age='S', bowstyle=bowstyle, gender='G')
            archer.save()
        # get or create competition entry
        competition_entry, created = CompetitionEntry.objects.get_or_create(competition=competition, archer=archer, bowstyle=bowstyle, novice=exp, age='S', club=club)
        session_entry, created = SessionEntry.objects.get_or_create(competition_entry=competition_entry, session_round=session_round)
        target_allocation, created = TargetAllocation.objects.get_or_create(session_entry=session_entry, boss=target[:-1], target=target[-1])
        print target[:-1], target[-1], archer


#clubs = sorted(list(clubs))
#for club in clubs:
#    club = club + ' Uni'
#    try:
#        club = Club.objects.get(short_name__iexact=club)
#        print club.pk, club.name
#        continue
#    except Club.DoesNotExist:
#        full_name = club + 'versity Archery Club'
#        abbreviation = ''.join([n[0] for n in full_name.split(' ')])
#        club = Club(name=full_name, short_name=club, abbreviation=abbreviation)
#        club.clean()
#        club.save()
#        print club.pk, club.name
#

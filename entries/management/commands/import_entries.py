"""Import entries from a CSV file.

This is naive of multi session entries for now.
"""
import csv
from optparse import make_option

from django.core.management import BaseCommand

from core.models import Archer, Club, Bowstyle
from entries.models import Competition, SessionRound, TargetAllocation


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--competition', '-c',
            action='store',
            dest='competition',
            help='Competition slug'
        ),
        make_option('--file', '-f',
            action='store',
            dest='file',
            help='File path to the csv'
        ),
        make_option('--dry-run', '-d',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Don\'t actually create anything'
        ),
        make_option('--clear',
            action='store_true',
            dest='clear',
            default=False,
            help='Clear the entire entries for this competition'
        ),
    )

    class ImportException(Exception):
        pass

    def error(self, msg):
        self.stderr.write('\x1b[31;1m%s\x1b[0m\n' % msg)
        raise self.ImportException

    def success(self, msg):
        self.stdout.write('\x1b[32;1m%s\x1b[0m\n' % msg)

    def info(self, msg):
        self.stdout.write('%s\n' % msg)

    def make_selection(self, iterable, msg='Choose: '):
        for i, o in enumerate(iterable, 1):
            self.info('%s: %s' % (i, o))
        valid = False
        while not valid:
            obj = input(msg)
            try:
                obj = iterable[int(obj) - 1]
            except (ValueError, IndexError):
                pass
            else:
                valid = True
        return obj

    def handle(self, *args, **kwargs):
        self.kwargs = kwargs
        self.data = []
        self.clubs = {}
        self.archers = set()
        try:
            self.setup()
            for entry in self.data:
                self.process_entry(entry)
        except self.ImportException:
            return

    def setup(self):
        try:
            self.competition = Competition.objects.get(slug=self.kwargs['competition'])
        except Competition.DoesNotExist:
            self.error('No such competition for slug %s' % self.kwargs['competition'])
        self.success('Importing entries for Competition: %s' % self.competition)

        with open(self.kwargs['file']) as f:
            reader = csv.DictReader(f)
            self.data = list(reader)

        if self.data:
            self.success('Found %s entries to import' % len(self.data))
        else:
            self.error('No data found')

        session_rounds = SessionRound.objects.filter(session__competition=self.competition)
        if not session_rounds:
            self.error('Competition has no session rounds')
        self.session = self.make_selection(session_rounds, 'Choose a session: ')
        self.success('Session is %s' % self.session)

        if self.kwargs['clear']:
            self.competition.competitionentry_set.all().delete()
            self.session.sessionentry_set.all().delete()

    def process_entry(self, entry):
        self.info('Importing archer %s' % entry['name'])

        if not entry['club']:
            return

        # Check the club
        club = None
        if entry['club'] in self.clubs:
            club = self.clubs[entry['club']]
        else:
            try:
                club = Club.objects.get(name=entry['club'])
            except Club.DoesNotExist:
                try:
                    club = Club.objects.get(name__icontains=entry['club'])
                except Club.DoesNotExist:
                    clubs = Club.objects.filter(name__icontains=entry['club'].replace('University of ', '').replace('University', ''))
                    club = self.make_selection(clubs, 'Choose a club: ')
                except Club.MultipleObjectsReturned:
                    clubs = Club.objects.filter(name__icontains=entry['club'])
                    club = self.make_selection(clubs, 'Choose a club: ')
            # TODO: handle people shooting for another club
            self.clubs[entry['club']] = club
        self.info('Club is %s' % club)

        bowstyle = Bowstyle.objects.get(name=entry['bowstyle'])
        gender = 'G' if entry['gender'].lower() == 'm' else 'L'
        age = entry.get('age', 'S')
        novice = entry.get('experience', 'E')

        # Try to find the archer
        entry['name'] = entry['name'].replace('  ', ' ').strip()
        try:
            archer = club.archer_set.get(name=entry['name'])
            if not archer.gender == gender:
                archer.gender = gender
                archer.save()
        except Archer.DoesNotExist:
            archer = Archer(name=entry['name'], bowstyle=bowstyle, gender=gender, club=club, age=age, novice=novice)
            archer.save()
        self.info('Archer is %s' % archer)

        # Check if they've entered already
        # entered = self.session.sessionentry_set.filter(archer=archer).exists()
        # if entered:
        #    self.info('Archer %s is already entered' % archer)
        #    return

        # Check archer's details
        # TODO

        # Make the entry
        if not self.kwargs['dry_run']:
            competition_entry = self.competition.competitionentry_set.create(
                archer=archer,
                club=club,
                bowstyle=bowstyle,
                age=age,
                novice=novice
            )
            session_entry = self.session.sessionentry_set.create(competition_entry=competition_entry)

        # Add the target allocation
        boss, target = entry['target'][:-1], entry['target'][-1]
        TargetAllocation.objects.create(boss=boss, target=target, session_entry=session_entry)

import csv
import json
from optparse import make_option

from django.core.management import BaseCommand

from entries.models import Competition
from scores.models import Score


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--competition', '-c',
            action='store',
            dest='competition',
            help='Competition slug'
        ),
    )

    class ExportException(Exception):
        pass

    def make_selection(self, iterable, msg='Choose: '):
        for i, o in enumerate(iterable, 1):
            self.info('%s: %s' % (i, o))
        valid = False
        while not valid:
            obj = raw_input(msg)
            try:
                obj = iterable[int(obj)-1]
            except (ValueError, IndexError):
                pass
            else:
                valid = True
        return obj

    def error(self, msg):
        self.stderr.write('\x1b[31;1m%s\x1b[0m\n' % msg)
        raise self.ExportException

    def success(self, msg):
        self.stdout.write('\x1b[32;1m%s\x1b[0m\n' % msg)

    def info(self, msg):
        self.stdout.write('%s\n' % msg)

    def handle(self, **kwargs):
        self.kwargs = kwargs
        try:
            self.setup()
            self.serialize(self.data)
        except self.ExportException:
            return

    def setup(self):
        try:
            self.competition = Competition.objects.get(slug=self.kwargs['competition'])
        except Competition.DoesNotExist:
            self.error('No such competition for slug %s' % self.kwargs['competition'])
        sessions = self.competition.session_set.all()
        self.session = self.make_selection(sessions, 'Choose a session: ')
        self.data = Score.objects.filter(target__session_entry__session_round__session=self.session).select_related()

    def serialize(self, data):
        writer = csv.writer(self.stdout)
        writer.writerow(['name', 'club', 'scores'])
        for score in data:
            if score.target.session_entry.competition_entry.novice == 'N':
                continue
            if score.target.session_entry.competition_entry.bowstyle.name == 'Compound':
                continue
            writer.writerow([
                score.target.session_entry.competition_entry.archer.name,
                score.target.session_entry.competition_entry.club.name,
                json.dumps(list(score.arrow_set.order_by('arrow_of_round').values_list('arrow_value', flat=True))),
            ])

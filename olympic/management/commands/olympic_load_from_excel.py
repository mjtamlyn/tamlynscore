from django.core.management import BaseCommand

from olympic.models import OlympicSessionRound, Seeding, Result, Match

import xlrd

class Command(BaseCommand):
    def handle(self, *args, **options):
        book = xlrd.open_workbook(args[0])

        for sheet in book.sheets():
            session_round = OlympicSessionRound.objects.get(pk=sheet.name)
            for n in range(2, sheet.nrows):
                row = sheet.row(n)
                seed = Seeding.objects.get(session_round=session_round, seed=row[0].value)
                level  = row[1].value
                match = Match.objects.match_for_seed(seed, level)
                score_column = 17 if session_round.shot_round.match_type == 'C' else 22
                score = row[score_column].value
                win_column = 20 if session_round.shot_round.match_type == 'C' else 25
                win = True if row[win_column].value == 'Y' else False

                result = Result(
                        seed=seed,
                        match=match,
                        total=score,
                        win=win
                )
                result.save()

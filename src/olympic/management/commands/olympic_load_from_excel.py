from django.core.management import BaseCommand

from olympic.models import OlympicSessionRound, Seeding

import xlrd

class Command(BaseCommand):
    def handle(self, *args, **options):
        book = xlrd.open_workbook(args[0])

        for sheet in book.sheets():
            session_round = OlympicSessionRound.objects.get(pk=sheet.name)
            for n in range(2, sheet.nrows)[:2]:
                row = sheet.row(n)
                seed = Seeding.objects.get(session_round=session_round, seed=row[0].value)
                print seed



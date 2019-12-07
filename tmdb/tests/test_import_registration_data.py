from pathlib import Path
from datetime import date
import os
import logging

from django.test import TestCase

from tmdb import models

LOGGER = logging.getLogger()

class TournamentImportTestCase(TestCase):
    @staticmethod
    def registration_data_filenames():
        data_dir = Path(__file__).parent / 'registration_test_data'
        filenames = [data_dir / fn for fn in sorted(os.listdir(data_dir))]
        for filename in filenames:
            basename = os.path.split(filename)[-1]
            year = int(basename[:4])
            tournament_num = int(basename[5])
            yield filename, year, tournament_num

    @staticmethod
    def import_tournament_data(filename, season, uniq_id=0):
        location = 'location-%d' %(uniq_id)
        date = season.start_date.replace(day=1 + uniq_id)
        url = 'http://ectc-online.org/%s/%d' %(season.id, uniq_id)
        tournament = models.Tournament.objects.create(
            location=location, date=date, registration_doc_url=url,
            season=season)
        with open(filename, 'r') as fh:
            tournament.import_registration_data(fh)
        return tournament

    def test_import_all_tournaments(self):
        TournamentImportTestCase.import_all_tournaments()

    @staticmethod
    def import_all_tournaments(verbose=False):
        filenames = TournamentImportTestCase.registration_data_filenames()
        for filename, year, tournament_num in filenames:
            if verbose:
                LOGGER.info("Importing %s", filename)
            season, created = models.Season.objects.get_or_create(
                start_date=date(year=year, month=9, day=1),
                end_date=date(year=year+1, month=9, day=1))
            TournamentImportTestCase.import_tournament_data(filename, season,
                uniq_id=tournament_num)

from pathlib import Path
from datetime import date
import os
import logging

from django.test import TestCase
from django.db.utils import IntegrityError

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
    def import_tournament(filename, year, uniq_id=0):
        season, created = models.Season.objects.get_or_create(
            start_date=date(year=year, month=9, day=1),
            end_date=date(year=year+1, month=9, day=1))
        location = 'location-%d' %(uniq_id)
        tournament_date = season.start_date.replace(day=1 + uniq_id)
        url = 'http://ectc-online.org/%s/%d' %(season.id, uniq_id)
        tournament = models.Tournament.objects.create(
            location=location, date=tournament_date, registration_doc_url=url,
            season=season)
        with open(filename, 'r') as fh:
            tournament.import_registration_data(fh)
        return tournament

    @staticmethod
    def import_all_tournaments(verbose=False):
        filenames = TournamentImportTestCase.registration_data_filenames()
        for filename, year, tournament_num in filenames:
            if verbose:
                LOGGER.info("Importing %s", filename)
            TournamentImportTestCase.import_tournament(filename, year,
                uniq_id=tournament_num)

    @staticmethod
    def import_single_tournament():
        tournament_data = TournamentImportTestCase.registration_data_filenames()
        filename, year, tournament_num = next(tournament_data)
        tournament = TournamentImportTestCase.import_tournament(
            filename, year, tournament_num)
        return tournament, filename

    def create_team_match(tournament):
        teams = models.SparringTeamRegistration.objects.filter(
            tournament_division__tournament=tournament)
        team_iter = iter(teams)
        for blue_team in team_iter:
            if blue_team.num_competitors() < 2:
                continue
            break
        for red_team in teams:
            if red_team.team.school == blue_team.team.school:
                continue
            if red_team.tournament_division != blue_team.tournament_division:
                continue
            if red_team.num_competitors() < 2:
                continue
            break

        return models.SparringTeamMatch.objects.create(
            division=blue_team.tournament_division, number=100, round_num=0,
            round_slot=0, blue_team=blue_team, red_team=red_team)

    def test_import_all_tournaments(self):
        TournamentImportTestCase.import_all_tournaments()

    def test_import_delete_import_tournament(self):
        tournament, filename = TournamentImportTestCase.import_single_tournament()
        tournament.drop_registration_data()
        with open(filename, 'r') as fh:
            tournament.import_registration_data(fh)

    def test_import_tournament_twice(self):
        tournament, filename = TournamentImportTestCase.import_single_tournament()
        with open(filename, 'r') as fh:
            self.assertRaises(IntegrityError,
                lambda: tournament.import_registration_data(fh))

    def test_drop_tournament_with_null_winning_team(self):
        tournament, filename = TournamentImportTestCase.import_single_tournament()
        team_match = TournamentImportTestCase.create_team_match(tournament)
        tournament.drop_registration_data()

    def test_drop_tournament_with_non_null_winning_team(self):
        tournament, filename = TournamentImportTestCase.import_single_tournament()
        team_match = TournamentImportTestCase.create_team_match(tournament)
        team_match.winning_team = team_match.blue_team
        team_match.save()
        tournament.drop_registration_data()

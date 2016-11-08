from django.core.management.base import BaseCommand
import csv
import os, sys
from tmdb.models import *

class ExportSeeds():
    def __init__(self):
        self.mensA_sheet = '/Users/andreaguatemala/Desktop/cornell_mensA_seeds.csv'
        self.womensA_sheet = '/Users/andreaguatemala/Desktop/cornell_womensA_seeds.csv'
        self.mensB_sheet = '/Users/andreaguatemala/Desktop/cornell_mensB_seeds.csv'
        self.womensB_sheet = '/Users/andreaguatemala/Desktop/cornell_womensB_seeds.csv'
        self.mensC_sheet = '/Users/andreaguatemala/Desktop/cornell_mensC_seeds.csv'
        self.womensC_sheet = '/Users/andreaguatemala/Desktop/cornell_womensC_seeds.csv'

        self.getSeeds(self.mensA_sheet, 1, 0)
        self.getSeeds(self.mensB_sheet, 1, 1)
        self.getSeeds(self.mensC_sheet, 1, 2)
        self.getSeeds(self.womensA_sheet, 0, 0)
        self.getSeeds(self.womensB_sheet, 0, 1)
        self.getSeeds(self.womensC_sheet, 0, 2)

    def getSeeds(self, sheet, sex, skill):
        self.tournament  = Tournament.objects.get(location="Cornell")
        self.div = Division.objects.get(sex=sex, skill_level = skill)
        self.tournamentDivision = TournamentDivision.objects.get(tournament= self.tournament, division=self.div)
        self.teams = TeamRegistration.objects.filter(tournament_division=self.tournamentDivision)

        self.data = []
        self.fieldnames = ["Teams", "Seeds"]

        for team in self.teams:
            string = str(team.team.school) + " " + str(team.team.division) + str(team.team.number) + "," + str(team.seed)
            self.data.append(string.split(","))

        with open(sheet, 'w', newline='') as csvfile:
            w = csv.writer(csvfile, delimiter=',')
            w.writerow(self.fieldnames)
            for i in self.data:
                w.writerow(i)

class Command(BaseCommand):
    help = 'Exports seeds'

    def handle(self, *args, **options):
        ExportSeeds()

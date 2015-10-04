#!/usr/bin/env python3
from django.core.management.base import BaseCommand
import tmdb.models as mdls

class LoadSampleTmdbData():
    def __init__(self):
        self.add_global_data()
        self.add_teams()
        self.add_matches()
        #self.add_match_participants()

    def add_global_data(self):
        mdls.BeltRank.create_tkd_belt_ranks()
        self.division = mdls.Division(name="Men's A",
                sex=mdls.SexField.FEMALE_DB_VAL)
        self.division.clean()
        self.division.save()

    def add_teams(self):
        for i in range(5):
            i += 1
            org = mdls.Organization(name="org" + str(i))
            org.clean()
            org.save()
            team = mdls.Team(number=1, organization=org, division=self.division)
            team.clean()
            team.save()

    def add_matches(self):
        self.finals_match = mdls.TeamMatch(division=self.division, number=1,
                parent_side=0, root_match=True)
        self.finals_match.clean()
        self.finals_match.save()

        self.semifinals1_match = mdls.TeamMatch(division=self.division,
                number=2, parent_side=0, parent=self.finals_match,
                root_match=False)
        self.semifinals1_match.red_team = mdls.Team.objects.get(pk=3)
        self.semifinals1_match.clean()
        self.semifinals1_match.save()

        self.semifinals2_match = mdls.TeamMatch(division=self.division,
                number=3, parent_side=1, parent=self.finals_match,
                root_match=False)
        self.semifinals2_match.blue_team = mdls.Team.objects.get(pk=4)
        self.semifinals2_match.red_team = mdls.Team.objects.get(pk=5)
        self.semifinals2_match.clean()
        self.semifinals2_match.save()

        self.quarterfinals_match = mdls.TeamMatch(division=self.division,
                number=4, parent_side=0, parent=self.semifinals1_match,
                root_match=False)
        self.quarterfinals_match.blue_team = mdls.Team.objects.get(pk=1)
        self.quarterfinals_match.red_team = mdls.Team.objects.get(pk=2)
        self.quarterfinals_match.clean()
        self.quarterfinals_match.save()


class Command(BaseCommand):
    help = 'Loads test data into the database - useful for testing the UI'

    def handle(self, *args, **options):
        LoadSampleTmdbData()

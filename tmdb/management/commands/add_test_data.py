#!/usr/bin/env python3
from django.core.management.base import BaseCommand
import tmdb.models as mdls
from datetime import date

class LoadSampleTmdbData():
    def __init__(self):
        self.num_teams = 5

        self.add_global_data()
        self.add_tournaments()
        self.add_orgs()
        self.add_teams()
        self.add_matches(self.divisions[0])

    def add_tournaments(self):
        # registration_doc_urls are just nonsense placefillers
        self.mit2015 = mdls.Tournament(date=date(year=2015, month=10, day=11),
                location="MIT",
                registration_doc_url="http://ectc-online.org/mit-2015")
        self.mit2015.save()
        self.cornell2015 = mdls.Tournament(date=date(year=2015, month=11,
                day=1), location="Cornell",
                registration_doc_url="http://ectc-online.org/cornell-2015")
        self.cornell2015.save()

    def add_orgs(self):
        self.orgs = {}
        for i in range(1, self.num_teams + 1):
            org = mdls.Organization(name="org" + str(i))
            org.clean()
            org.save()
            self.orgs[i] = org

    def add_global_data(self):
        if mdls.BeltRank is None:
            mdls.BeltRank.create_tkd_belt_ranks()
        self.divisions = []

        division = mdls.Division(sex=mdls.SexField.MALE_DB_VAL,
            skill_level=mdls.DivisionSkillField.A_TEAM_VAL)
        division.clean()
        division.save()
        self.divisions.append(division)

        division = mdls.Division(sex=mdls.SexField.FEMALE_DB_VAL,
            skill_level=mdls.DivisionSkillField.A_TEAM_VAL)
        division.clean()
        division.save()
        self.divisions.append(division)

    def add_teams(self):
        for division in self.divisions:
            for i in range(1, self.num_teams + 1):
                org = self.orgs[i]
                team = mdls.Team(number=1, organization=org, division=division)
                team.clean()
                team.save()

    def add_matches(self, division):
        self.finals_match = mdls.TeamMatch(division=division, number=1,
                parent_side=0, root_match=True)
        self.finals_match.clean()
        self.finals_match.save()

        self.semifinals1_match = mdls.TeamMatch(division=division, number=2,
                parent_side=0, parent=self.finals_match, root_match=False)
        self.semifinals1_match.red_team = mdls.Team.objects.get(pk=3)
        self.semifinals1_match.clean()
        self.semifinals1_match.save()

        self.semifinals2_match = mdls.TeamMatch(division=division, number=3,
                parent_side=1, parent=self.finals_match, root_match=False)
        self.semifinals2_match.blue_team = mdls.Team.objects.get(pk=4)
        self.semifinals2_match.red_team = mdls.Team.objects.get(pk=5)
        self.semifinals2_match.clean()
        self.semifinals2_match.save()

        self.quarterfinals_match = mdls.TeamMatch(division=division, number=4,
                parent_side=0, parent=self.semifinals1_match, root_match=False)
        self.quarterfinals_match.blue_team = mdls.Team.objects.get(pk=1)
        self.quarterfinals_match.red_team = mdls.Team.objects.get(pk=2)
        self.quarterfinals_match.clean()
        self.quarterfinals_match.save()


class Command(BaseCommand):
    help = 'Loads test data into the database - useful for testing the UI'

    def handle(self, *args, **options):
        LoadSampleTmdbData()

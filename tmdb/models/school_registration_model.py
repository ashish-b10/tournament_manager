"""
School Registration Model

Last Updated: 07-25-2017
"""

from django.db import models

from .fields_model import *
from .tournament_model import *
from .school_model import *


class SchoolRegistration(models.Model):
    tournament = models.ForeignKey(Tournament)
    school = models.ForeignKey(School)
    registration_doc_url = models.URLField(unique=True)
    imported = models.BooleanField(default=False)

    class Meta:
        unique_together = (('tournament', 'school'),)

    def __str__(self):
        return '%s/%s' % (self.tournament, self.school,)

    def download_school_registration(self):
        from ectc_registration import GoogleDocsDownloader
        from ectc_registration import SchoolRegistrationExtractor
        try:
            creds = ConfigurationSetting.objects.get(
                key=ConfigurationSetting.REGISTRATION_CREDENTIALS).value
        except ConfigurationSetting.DoesNotExist:
            raise IntegrityError("Registration credentials have not been"
                                 + " provided")
        downloader = GoogleDocsDownloader(creds_json=creds)
        url = self.registration_doc_url
        registration_extractor = SchoolRegistrationExtractor(
            school_name=self.school.name, registration_doc_url=url)
        registration_extractor.extract(downloader)
        return registration_extractor

    def save_extracted_competitors(self, extracted_competitors):
        model_competitors = {}
        for c in extracted_competitors:
            weight = None
            if 'weight' in c:
                weight = float(c['weight'])
            try:
                belt_rank = BeltRankField.value(c['rank'])
            except IndexError:
                raise ValidationError("Unexpected belt rank value: "
                                      + c['rank'])
            competitor = Competitor.objects.get_or_create(name=c['name'],
                                                          registration=self, defaults={
                    'sex': c['sex'],
                    'belt_rank': belt_rank,
                    'weight': weight,
                })[0]
            model_competitors[competitor.name] = competitor
        return model_competitors

    @staticmethod
    def _parse_division(division_name):
        sex = skill = None
        if division_name == "Mens_A":
            sex = SexField.MALE
            skill = DivisionLevelField.A_TEAM_VAL
        elif division_name == "Mens_B":
            sex = SexField.MALE
            skill = DivisionLevelField.B_TEAM_VAL
        elif division_name == "Mens_C":
            sex = SexField.MALE
            skill = DivisionLevelField.C_TEAM_VAL
        elif division_name == "Womens_A":
            sex = SexField.FEMALE
            skill = DivisionLevelField.A_TEAM_VAL
        elif division_name == "Womens_B":
            sex = SexField.FEMALE
            skill = DivisionLevelField.B_TEAM_VAL
        elif division_name == "Womens_C":
            sex = SexField.FEMALE
            skill = DivisionLevelField.C_TEAM_VAL
        if sex is None or skill is None:
            raise ValueError("Invalid division supplied: %s" % (division_name,))
        return Division.objects.get(sex=sex, skill_level=skill)

    def check_roster_competitors(self, team_registration, roster, competitors):
        competitor_names = {c for c in roster if c}
        missing_competitors = competitor_names - set(competitors.keys())
        if missing_competitors:
            raise Competitor.DoesNotExist("Could not find Competitor(s): ["
                                          + ", ".join(missing_competitors) + "] for team ["
                                          + str(team_registration.team) + "]")

    def save_team_roster(self, team_registration, roster, competitors):
        self.check_roster_competitors(team_registration, roster, competitors)
        if roster[0]:
            team_registration.lightweight = competitors[roster[0]]
        if roster[1]:
            team_registration.middleweight = competitors[roster[1]]
        if roster[2]:
            team_registration.heavyweight = competitors[roster[2]]
        if roster[3]:
            team_registration.alternate1 = competitors[roster[3]]
        if roster[4]:
            team_registration.alternate2 = competitors[roster[4]]
        team_registration.clean()
        team_registration.save()

    def save_extracted_teams(self, teams, competitors):
        for division_name, rosters in teams.items():
            division = self._parse_division(division_name)
            for team_num, roster in enumerate(rosters):
                if not roster:
                    continue
                roster = [r.strip() for r in roster]
                team = Team.objects.get_or_create(school=self.school,
                                                  division=division, number=team_num + 1)[0]
                tournament_division = TournamentDivision.objects.get(
                    tournament=self.tournament, division=division)
                team_reg = TeamRegistration.objects.get_or_create(
                    tournament_division=tournament_division, team=team)[0]
                self.save_team_roster(team_reg, roster, competitors)

    def drop_competitors_and_teams(self):
        if not self.imported:
            raise IntegrityError(("%s is not imported" % (self)
                                  + " - and must be imported before it is dropped"))

        TeamRegistration.objects.filter(
            tournament_division__tournament=self.tournament,
            team__school=self.school).delete()
        Competitor.objects.filter(registration=self).delete()
        self.imported = False
        self.save()

    def import_competitors_and_teams(self, reimport=False):
        if reimport and self.imported:
            self.drop_competitors_and_teams()

        if self.imported:
            raise IntegrityError(("%s is already imported" % (self.school)
                                  + " and will not be reimported"))

        school_extracted_data = self.download_school_registration()
        competitors = self.save_extracted_competitors(
            school_extracted_data.extracted_competitors)
        self.save_extracted_teams(school_extracted_data.teams, competitors)
        self.imported = True
        self.save()

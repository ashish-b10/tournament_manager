from collections import Counter

from tmdb import models

class SchoolRegistrationValidator:
    def __init__(self, school_registration, extracted_data):
        self.extracted_data = extracted_data
        self.school_registration = school_registration
        self.competitors_by_name = {c['name']:c
                for c in self.extracted_data.extracted_competitors}

    def validate(self):
        errors = []
        errors += self.validate_unique_competitor_names()
        errors += self.validate_belt_ranks_and_sexes()
        errors += self.validate_teams()
        return errors

    def validate_unique_competitor_names(self):
        name_counts = Counter(i['name']
                for i in self.extracted_data.extracted_competitors)
        duplicate_names = [(name, count) for name,count in name_counts.items()
                if count > 1]
        errors = []
        for name,count in duplicate_names:
            error_text = "Competitor named `%s` was listed %d times on the 'Weigh-Ins' sheet. Remove the duplicate entries or change the names." %(
                    name, count,)
            errors.append(models.SchoolRegistrationError(
                    school_registration=self.school_registration,
                    error_text=error_text))
        return errors

    def validate_belt_ranks_and_sexes(self):
        errors = []
        belt_ranks = ', '.join(
                models.BeltRankField.BELT_RANK_VALUES.keys())
        sex_values = ', '.join(models.SexField.SEX_LABELS.keys())
        for competitor in self.extracted_data.extracted_competitors:
            try:
                models.BeltRankField.value(competitor['rank'])
            except KeyError:
                error_text = "Invalid belt rank provdided for %s: `%s`. Edit column E of the Weigh-Ins sheet with a valid belt rank (%s)" %(
                        competitor['name'], competitor['rank'], belt_ranks)
                errors.append(models.SchoolRegistrationError(
                        school_registration=self.school_registration,
                        error_text=error_text))

            try:
                models.SexField.label(competitor['sex'])
            except KeyError:
                error_text = "Invalid sex provided for %s: `%s`. Edit column G of the Weigh-Ins sheet with a valid sex (%s)" %(
                        competitor['name'], competitor['sex'], sex_values)
                errors.append(models.SchoolRegistrationError(
                        school_registration=self.school_registration,
                        error_text=error_text))
        return errors

    def validate_division_team(self, division_name, team, team_num):
        errors = []
        team_name = "%s %d" %(division_name, team_num)
        for roster_name in team:
            if not roster_name:
                continue
            roster_name = roster_name.strip()
            if roster_name not in self.competitors_by_name:
                error_text = "{roster_name} is assigned to {team_name} but was not on the roster. Either add {roster_name} to the Weigh-Ins sheet or remove them from the {division_name} sheet.".format(
                        roster_name=roster_name,
                        team_name=team_name,
                        division_name=division_name)
                errors.append(models.SchoolRegistrationError(
                        school_registration=self.school_registration,
                        error_text = error_text))
        return errors

    def validate_division_teams(self, division_name, division_teams):
        errors = []
        for team_num, team in enumerate(division_teams, start=1):
            if not team:
                continue
            errors += self.validate_division_team(division_name, team,
                    team_num)
        return errors

    def validate_teams(self):
        errors = []
        for division_name, division_teams in self.extracted_data.teams.items():
            errors += self.validate_division_teams(division_name,
                    division_teams)
        return errors

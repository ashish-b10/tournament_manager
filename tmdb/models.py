from django.db import models
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
import decimal
from itertools import product
from django.template.defaultfilters import slugify

from tmdb.util import Bracket

from django_enumfield import enum

class SexEnum(enum.Enum):
    F = 0
    M = 1

    labels = {
        F: 'Female',
        M: 'Male',
    }

class DivisionLevelEnum(enum.Enum):
    A = 0
    B = 1
    C = 2

    labels = {
        A: 'A-team',
        B: 'B-team',
        C: 'C-team',
    }

class BeltRankEnum(enum.Enum):
    WHITE = 0
    YELLOW = 1
    ORANGE = 2
    GREEN = 3
    BLUE = 4
    PURPLE = 5
    BROWN = 6
    RED = 7
    BLACK = 8

    labels = {
        WHITE: 'White',
        YELLOW: 'Yellow',
        ORANGE: 'Orange',
        GREEN: 'Green',
        BLUE: 'Blue',
        PURPLE: 'Purple',
        BROWN: 'Brown',
        RED: 'Red',
        BLACK: 'Black',
    }

class DivisionSkillField(models.CharField):
    A_TEAM_VAL = 'A'
    B_TEAM_VAL = 'B'
    C_TEAM_VAL = 'C'
    choices = (
        (A_TEAM_VAL, 'A-team'),
        (B_TEAM_VAL, 'B-team'),
        (C_TEAM_VAL, 'C-team'),
    )
    _division_skills_names = dict(choices)

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 1
        super(DivisionSkillField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value in DivisionSkillField._division_skills_names.keys():
            raise(ValidationError("Invalid DivisionSkillField value: "
                    + value))
        return value

    def __str__(self):
        return self._division_skills_names[self.division_skill]

class WeightField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 4
        kwargs['decimal_places'] = 1
        super(WeightField, self).__init__(*args, **kwargs)

class Tournament(models.Model):
    slug = models.SlugField(unique=True)
    location = models.CharField(max_length=127)
    date = models.DateField()
    registration_doc_url = models.URLField(unique=True)
    imported = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        new_tournament = False
        if not self.id:
            self.slug = self.slugify()
            new_tournament = True

        super(Tournament, self).save(*args, **kwargs)

        if new_tournament:
            self.create_divisions()

    def slugify(self):
        return slugify(self.location) + '-' + slugify(self.date)

    def create_divisions(self):
        for sex, skill_level in product(('M', 'F'),('A', 'B', 'C',),):
            sex = SexEnum.get(sex).value
            skill_level = DivisionLevelEnum.get(skill_level).value
            division = Division.objects.filter(sex=sex,
                    skill_level=skill_level).first()
            if division is None:
                division = Division(sex=sex, skill_level=skill_level)
                division.clean()
                division.save()
            td = TournamentDivision(tournament=self, division=division)
            td.clean()
            td.save()

    def __str__(self):
        return self.slug if self.slug else self.slugify()

    def download_registration(self):
        """Downloads registration spreadsheet from registration_doc_url."""
        from ectc_registration import GoogleDocsDownloader
        from ectc_registration import GoogleDriveSpreadsheet
        from ectc_registration import RegistrationExtractor

        try:
            creds = ConfigurationSetting.objects.get(
                    key=ConfigurationSetting.REGISTRATION_CREDENTIALS).value
        except ConfigurationSetting.DoesNotExist:
            raise IntegrityError("Registration credentials have not been"
                    + " provided")
        doc_url = self.registration_doc_url
        doc_key = GoogleDocsDownloader.extract_file_id(doc_url)
        downloader = GoogleDocsDownloader(creds_json=creds)
        workbook = GoogleDriveSpreadsheet(downloader, doc_key)
        reg_extractor = RegistrationExtractor(workbook)
        return reg_extractor.get_registration_workbooks()

    def save_downloaded_school(self, school):
        school_object = School.objects.filter(
                name=school.school_name).first()
        if school_object is None:
            school_object = School(name=school.school_name)
            school_object.clean()
            school_object.save()
        registration = SchoolRegistration(tournament=self,
                school=school_object,
                registration_doc_url=school.registration_doc_url)
        registration.clean()
        registration.save()

    def save_downloaded_schools(self, schools):
        for school in schools:
            self.save_downloaded_school(school)

    def import_school_registrations(self):
        """Imports a school's registration information from
        registration_doc_url."""
        if self.imported:
            raise IntegrityError(("%s is already imported" %(self)
                    + " - and cannot be imported again"))
        registered_schools = self.download_registration()
        self.save_downloaded_schools(registered_schools)

        self.imported = True
        self.save()

class School(models.Model):
    name = models.CharField(max_length=127, unique=True)
    tournaments = models.ManyToManyField('Tournament',
            through='SchoolRegistration')
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        new_school = False
        if not self.id:
            new_school = True
            self.slug = self.slugify()

        super(School, self).save(*args, **kwargs)

        if new_school:
            self.create_teams()

    def create_teams(self):
        for sex, skill_level in product(('M', 'F'),('A', 'B', 'C',),):
            sex = SexEnum.get(sex).value
            skill_level = DivisionLevelEnum.get(skill_level).value
            division = Division.objects.filter(sex=sex,
                    skill_level=skill_level).first()
            if division is None:
                division = Division(sex=sex, skill_level=skill_level)
                division.clean()
                division.save()
            self.create_division_teams(division)

    def create_division_teams(self, division):
        for team_num in range(1,11):
            team = Team(school=self, division=division, number=team_num)
            team.clean()
            team.save()

    def slugify(self):
        return slugify(self.name)

    def __str__(self):
        return self.name

class SchoolRegistration(models.Model):
    tournament = models.ForeignKey(Tournament)
    school = models.ForeignKey(School)
    registration_doc_url = models.URLField(unique=True)
    imported = models.BooleanField(default=False)

    class Meta:
        unique_together = (('tournament', 'school'),)

    def __str__(self):
        return '%s/%s' %(self.tournament, self.school,)

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
            competitor = Competitor.objects.get_or_create(name=c['name'],
                    registration=self, defaults={
                            'sex': SexEnum.get(c['sex']).value,
                            'belt_rank': BeltRankEnum.get(c['rank']).value,
                            'weight': weight,
                    })[0]
            model_competitors[competitor.name] = competitor
        return model_competitors

    @staticmethod
    def _parse_division(division_name):
        sex = skill = None
        if division_name == "Mens_A":
            sex = SexEnum.get('M').value
            skill = DivisionLevelEnum.get('A').value
        elif division_name == "Mens_B":
            sex = SexEnum.get('M').value
            skill = DivisionLevelEnum.get('B').value
        elif division_name == "Mens_C":
            sex = SexEnum.get('M').value
            skill = DivisionLevelEnum.get('C').value
        elif division_name == "Womens_A":
            sex = SexEnum.get('F').value
            skill = DivisionLevelEnum.get('A').value
        elif division_name == "Womens_B":
            skill = DivisionLevelEnum.get('B').value
            sex = SexEnum.get('F').value
        elif division_name == "Womens_C":
            sex = SexEnum.get('F').value
            skill = DivisionLevelEnum.get('C').value
        if sex is None or skill is None:
            raise ValueError("Invalid division supplied: %s" %(division_name,))
        return Division.objects.get(sex=sex, skill_level = skill)

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
                team = Team.objects.get_or_create(school=self.school,
                        division=division, number=team_num+1)[0]
                tournament_division = TournamentDivision.objects.get(
                        tournament=self.tournament, division=division)
                team_reg = TeamRegistration.objects.get_or_create(
                        tournament_division=tournament_division, team=team)[0]
                self.save_team_roster(team_reg, roster, competitors)

    def drop_competitors_and_teams(self):
        if not self.imported:
            raise IntegrityError(("%s is not imported" %(self)
                    + " - and must be imported before it is dropped"))

        TeamRegistration.objects.filter(
                tournament_division__tournament=self.tournament,
                team__school=self.school).delete()
        Competitor.objects.filter(registration=self).delete()
        self.imported = False
        self.save()

    def import_competitors_and_teams(self):
        if self.imported:
            raise IntegrityError(("%s is already imported" %(self)
                    + " - and cannot be imported again"))

        school_extracted_data = self.download_school_registration()
        competitors = self.save_extracted_competitors(
                school_extracted_data.extracted_competitors)
        self.save_extracted_teams(school_extracted_data.teams, competitors)
        self.imported = True
        self.save()

class Division(models.Model):
    sex = enum.EnumField(SexEnum)
    skill_level = enum.EnumField(DivisionLevelEnum)
    slug = models.SlugField(unique=True)
    tournaments = models.ManyToManyField('Tournament',
            through='TournamentDivision')

    class Meta:
        unique_together = (("sex", "skill_level"),)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = self.slugify()
        super(Division, self).save(*args, **kwargs)

    def slugify(self):
        return slugify(str(self))

    def __str__(self):
        if self.sex == SexEnum.F: sex_name = "Women's"
        if self.sex == SexEnum.M: sex_name = "Men's"
        return sex_name + " " + DivisionLevelEnum.label(self.skill_level)

    def match_number_start_val(self):
        if self.skill_level == DivisionLevelEnum.A:
            start_val = 100
        elif self.skill_level == DivisionLevelEnum.B:
            start_val = 300
        elif self.skill_level == DivisionLevelEnum.C:
            start_val = 500
        return start_val + (100 if self.sex == SexEnum.F else 0)

class TournamentDivision(models.Model):
    tournament = models.ForeignKey(Tournament)
    division = models.ForeignKey(Division)

    class Meta:
        unique_together = (('tournament', 'division'),)

    def __str__(self):
        return "%s" %(self.division)

    def __repr__(self):
        return "%s (%s)" %(self.division, self.tournament)

class TournamentDivisionBeltRanks(models.Model):
    belt_rank = enum.EnumField(BeltRankEnum)
    tournament_division = models.ForeignKey(TournamentDivision)

class Competitor(models.Model):
    """ A person who may compete in a tournament. """
    name = models.CharField(max_length=127)
    sex = enum.EnumField(SexEnum)
    belt_rank = enum.EnumField(BeltRankEnum)
    weight = WeightField(null=True, blank=True)
    registration = models.ForeignKey(SchoolRegistration)

    def belt_rank_label(self):
        return BeltRankEnum.label(self.belt_rank)

    def sex_label(self):
        return SexEnum.label(self.sex)

    def __str__(self):
        return "%s (%s)" % (self.name, self.registration.school)

    class Meta:
        unique_together = (("name", "registration"),)

class Team(models.Model):
    school = models.ForeignKey(School)
    division = models.ForeignKey(Division)
    number = models.SmallIntegerField()
    registrations = models.ManyToManyField(TournamentDivision,
            through="TeamRegistration")

    class Meta:
        unique_together = (('school', 'division', 'number',),)

    def __str__(self):
        return "%s %s %d" %(str(self.school), str(self.division), self.number,)

#TODO team.division must equal tournament_division.division
class TeamRegistration(models.Model):
    tournament_division = models.ForeignKey(TournamentDivision)
    team = models.ForeignKey(Team)
    seed = models.PositiveSmallIntegerField(null=True, blank=True)
    lightweight = models.ForeignKey(Competitor, null=True, blank=True,
            related_name="lightweight")
    middleweight = models.ForeignKey(Competitor, null=True, blank=True,
            related_name="middleweight")
    heavyweight = models.ForeignKey(Competitor, null=True, blank=True,
            related_name="heavyweight")
    alternate1 = models.ForeignKey(Competitor, null=True, blank=True,
            related_name="alternate1")
    alternate2 = models.ForeignKey(Competitor, null=True, blank=True,
            related_name="alternate2")

    class Meta:
        unique_together = (('tournament_division', 'team'),)

    def __str__(self):
        return "%s" %(str(self.team))

    def __repr__(self):
        return "%s (%s)" %(str(self.team),
                str(self.tournament_division.tournament),)

class TeamMatch(models.Model):
    """ A match between two (or more?) Teams in a Division. A TeamMatch
    can have multiple CompetitorMatches.

    There is a uniqueness constraint on parent and parent_side. If the
    match is the root match of the division, then parent must be null,
    parent_side must be set to 0, and root_match must be set to true.
    Otherwise, parent_side and parent should be non-null and root_match
    must be set to false. There should only be one match for each
    division for which root_match is True.

    Attributes:
        division        The TournamentDivision that the match belongs to
        number          The match number (unique amongst all
                        TeamMatches)
        parent          The TeamMatch the winner will advance to
        parent_side     The side of the parent the winner will play on
        root_match      Whether this is the root_match of the division
        blue_team       The Team fighting in blue for this match
        red_team        The Team fighting in red for this match
        ring_number     The number of the assigned ring
        ring_assignment_time
                        The time at which the ring was assigned
        winning_team    The winner of the TeamMatch
    """
    division = models.ForeignKey(TournamentDivision)
    number = models.PositiveIntegerField(unique=True)
    parent = models.ForeignKey('self', blank=True, null=True)
    parent_side = models.IntegerField()
    root_match = models.BooleanField()
    blue_team = models.ForeignKey(TeamRegistration, related_name="blue_team",
            blank=True, null=True)
    red_team = models.ForeignKey(TeamRegistration, related_name="red_team",
            blank=True, null=True)
    ring_number = models.PositiveIntegerField(blank=True, null=True)
    ring_assignment_time = models.DateTimeField(blank=True, null=True)
    winning_team = models.ForeignKey(TeamRegistration, blank=True, null=True,
            related_name="winning_team")
    class Meta:
        unique_together = (("parent", "parent_side"), ("division", "number",),)

    def __str__(self):
        return "Match #" + str(self.number)

    def get_root_match(self):
        """ Return the root match of this match's division. """
        root_matches = TeamMatch.objects.filter(
                division=self.division).filter(root_match=True)
        if not root_matches:
            return None
        return root_matches.get()

    def get_child_match(self, slot_side):
        try:
            return TeamMatch.objects.get(parent=self, parent_side=slot_side)
        except TeamMatch.DoesNotExist:
            return None

    @staticmethod
    def create_matches_from_seeds(tournament_division):
        TeamMatch.objects.filter(division=tournament_division).delete()
        seeded_teams = TeamRegistration.objects.filter(
                tournament_division=tournament_division, seed__isnull=False)
        seeds = {team.seed:team for team in seeded_teams}
        start_val = tournament_division.division.match_number_start_val()
        bracket = Bracket(seeds, match_number_start_val=start_val)
        for bracket_match in bracket.bfs(seeds=False):
            match = TeamMatch(division=tournament_division,
                    number=bracket_match.number,
                    parent_side=bracket_match.parent_side,
                    root_match=bracket_match.is_root)

            if not bracket_match.is_root:
                match.parent = TeamMatch.objects.get(
                        number=bracket_match.parent.number)

            try:
                match.blue_team = bracket_match.blue_team.team
            except AttributeError:
                pass
            try:
                bracket_match.red_team
            except: pass
            try:
                match.red_team = bracket_match.red_team.team
            except AttributeError:
                pass

            match.clean()
            match.save()

    def validate_single_root_match(self):
        """ Validate that only one match in a division is the root. """
        if not self.root_match: return
        root_match = self.get_root_match()
        if root_match is not None and root_match != self:
            raise ValidationError("Division %s already has a root match"
                    %(self.division))
        if self.parent is not None:
            raise ValidationError("Root match must have null parent")
        if self.parent_side != 0:
            raise ValidationError("parent_side must be 0 for root match")

    def validate_team_match(self):
        self.update_parent_match()

    def update_parent_match(self):
        # set winning_team as blue_team or red_team in parent_match
        if not self.parent:
            return
        if self.parent_side == 0:
            self.parent.blue_team = self.winning_team
        elif self.parent_side == 1:
            self.parent.red_team = self.winning_team
        #self.parent.clean() #cannot call clean because child is not saved yet
        self.parent.save()

    def clean(self, *args, **kwargs):
        self.validate_team_match()

class ConfigurationSetting(models.Model):
    key = models.TextField(unique=True)
    value = models.TextField()
    REGISTRATION_CREDENTIALS = 'registration_credentials'

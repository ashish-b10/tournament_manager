from django.db import models
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
import decimal
from itertools import product
from django.template.defaultfilters import slugify

from tmdb.util import BracketGenerator, SlotAssigner

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
        A: 'A',
        B: 'B',
        C: 'C',
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
        return "%s Tournament (%s)" %(
                self.location, self.date.strftime("%Y %b %d"))

    def __repr__(self):
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
        return start_val + (100 if self.sex == SexEnum.F else 0) + 1

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
        return "%s %s%d" %(str(self.school), str(self.division), self.number,)

#TODO team.division must equal tournament_division.division
class TeamRegistration(models.Model):
    tournament_division = models.ForeignKey(TournamentDivision)
    team = models.ForeignKey(Team)
    seed = models.PositiveSmallIntegerField(null=True, blank=True)
    points = models.PositiveIntegerField(null=True, blank=True)
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
        unique_together = (('tournament_division', 'team'),
                ('tournament_division', 'seed'),)

    def __get_competitors_str(self):
        lightweight = "L" if self.lightweight else ""
        middleweight = "M" if self.middleweight else ""
        heavyweight = "H" if self.heavyweight else ""
        if not lightweight and not middleweight and not heavyweight:
            return ""
        return "(" + lightweight + middleweight + heavyweight + ")"

    def __str__(self):
        competitors_str = self.__get_competitors_str()
        if competitors_str:
            competitors_str = " " + competitors_str
        return "%s%s" %(str(self.team), competitors_str)

    def __repr__(self):
        return "%s (%s)" %(str(self.team),
                str(self.tournament_division.tournament),)

    def bracket_str(self):
        if not self.seed:
            return str(self)
        return "[%d] %s" %(self.seed, str(self))

    def num_competitors(self):
        return sum(map(lambda x: x is not None,
                [self.lightweight, self.middleweight, self.heavyweight]))

    @classmethod
    def get_teams_with_assigned_slots(cls, tournament_division):
        """
        Assigns all teams in tournament_division to a slot in the
        bracket. Returns a dict of {team:seed}.
        """
        teams = cls.objects.filter(tournament_division=tournament_division).order_by('team__number').order_by('team__school')
        get_num_competitors = lambda team: team.num_competitors()
        slot_assigner = SlotAssigner(list(teams), 4,
                get_school_name = lambda team: team.team.school.name,
                get_points = lambda team: team.points if team.points else 0)
        for team in teams:
            team.seed = slot_assigner.slots_by_team.get(team)
        return teams

    @classmethod
    def get_teams_without_assigned_slot(cls, tournament_division):
        """
        Returns a list of teams that do not have a slot in the bracket.

        Currently, the condition for this is TeamRegistration.seed is
        empty.
        """
        return cls.objects.filter(
                tournament_division=tournament_division, seed__isnull=True) \
                .order_by('team__school__name', 'team__number')

class TeamMatch(models.Model):
    """ A match between two (or more?) Teams in a Division. A TeamMatch
    can have multiple CompetitorMatches.

    Attributes:
        division        The TournamentDivision that the match belongs to
        number          The match number (unique amongst all
                        TeamMatches)
        round_num       Which round is this match in terms of distance
                        from the final? (0 means this match is the
                        final, 1 means this match is the semi-final,
                        etc.). The number of matches in a given round is
                        (2**round_num)
        round_slot      Which slot (from top to bottom) does this match
                        belong to in its round? 0 means top of the
                        bracket, 1 = second from the top of the round,
                        and (2**round_num - 1) = bottom of the round.
        blue_team       The Team fighting in blue for this match
        red_team        The Team fighting in red for this match
        ring_number     The number of the assigned ring
        ring_assignment_time
                        The time at which the ring was assigned
        winning_team    The winner of the TeamMatch
    """
    division = models.ForeignKey(TournamentDivision)
    number = models.PositiveIntegerField()
    round_num = models.SmallIntegerField()
    round_slot = models.IntegerField()
    blue_team = models.ForeignKey(TeamRegistration, related_name="blue_team",
            blank=True, null=True)
    red_team = models.ForeignKey(TeamRegistration, related_name="red_team",
            blank=True, null=True)
    ring_number = models.PositiveIntegerField(blank=True, null=True)
    ring_assignment_time = models.DateTimeField(blank=True, null=True)
    winning_team = models.ForeignKey(TeamRegistration, blank=True, null=True,
            related_name="winning_team")
    class Meta:
        unique_together = (
                ("division", "round_num", "round_slot"),
                ("division", "number",),
        )

    def __str__(self):
        return "Match #" + str(self.number)

    def get_previous_round_matches(self):
        upper_match_query = TeamMatch.objects.filter(division=self.division,
                round_num=self.round_num + 1, round_slot=2*self.round_slot)
        lower_match_query = TeamMatch.objects.filter(division=self.division,
                round_num=self.round_num + 1, round_slot=2*self.round_slot + 1)
        return [upper_match_query.first(), lower_match_query.first()]

    def get_next_round_match(self):
        try:
            return TeamMatch.objects.get(division=self.division,
                    round_num=self.round_num-1,
                    round_slot = self.round_slot / 2)
        except TeamMatch.DoesNotExist:
            return None

    def update_winning_team(self):
        if self.round_num != 0:
            parent_match = self.get_next_round_match()
            if self.round_slot % 2:
                parent_match.red_team = self.winning_team
            else:
                parent_match.blue_team = self.winning_team
            parent_match.clean()
            parent_match.save()

    def clean(self, *args, **kwargs):
        self.update_winning_team()

    @staticmethod
    def create_matches_from_slots(tournament_division):
        TeamMatch.objects.filter(division=tournament_division).delete()
        seeded_teams = TeamRegistration.objects.filter(
                tournament_division=tournament_division, seed__isnull=False)
        seeds = {team.seed:team for team in seeded_teams}
        start_val = tournament_division.division.match_number_start_val()
        bracket = BracketGenerator(seeds, match_number_start_val=start_val)
        for bracket_match in bracket.bfs(seeds=False):
            match = TeamMatch(division=tournament_division,
                    number=bracket_match.number,
                    round_num = bracket_match.round_num,
                    round_slot = bracket_match.round_slot)

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

class ConfigurationSetting(models.Model):
    key = models.TextField(unique=True)
    value = models.TextField()
    REGISTRATION_CREDENTIALS = 'registration_credentials'

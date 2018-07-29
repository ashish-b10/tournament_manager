from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from itertools import product
from django.template.defaultfilters import slugify

from tmdb.util import BracketGenerator, SlotAssigner
from .school_registration_validator import SchoolRegistrationValidator

class SchoolValidationError(IntegrityError): pass

class SexField(models.CharField):
    FEMALE = 'F'
    MALE = 'M'
    SEX_CHOICES = (
        (FEMALE, 'Female'),
        (MALE, 'Male'),
    )

    SEX_LABELS = dict(SEX_CHOICES)
    SEX_VALUES = {v.lower():k for k,v in SEX_LABELS.items()}

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 1
        kwargs['choices'] = SexField.SEX_CHOICES
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if not value in SexField.SEX_LABELS:
            raise(ValidationError("Invalid SexField value: " + value))
        return value

    @staticmethod
    def label(l):
        return SexField.SEX_LABELS[l]

    @staticmethod
    def value(v):
        return SexField.SEX_VALUES[v.lower()]

class DivisionLevelField(models.CharField):
    A_TEAM_VAL = 'A'
    B_TEAM_VAL = 'B'
    C_TEAM_VAL = 'C'
    DIVISION_LEVEL_CHOICES = (
        (A_TEAM_VAL, 'A-team'),
        (B_TEAM_VAL, 'B-team'),
        (C_TEAM_VAL, 'C-team'),
    )

    DIVISION_LEVEL_LABELS = dict(DIVISION_LEVEL_CHOICES)
    DIVISION_LEVEL_VALUES = {v.lower():k for k,v in DIVISION_LEVEL_LABELS.items()}

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 1
        kwargs['choices'] = DivisionLevelField.DIVISION_LEVEL_CHOICES
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if not value in DivisionLevelField.DIVISION_LEVEL_LABELS:
            raise(ValidationError("Invalid DivisionLevelField value: "
                    + value))
        return value

    @staticmethod
    def label(l):
        return DivisionLevelField.DIVISION_LEVEL_LABELS[l]

    @staticmethod
    def value(v):
        return DivisionLevelField.DIVISION_LEVEL_VALUES[v.lower()]

class BeltRankField(models.CharField):
    WHITE = 'WH'
    YELLOW = 'YL'
    ORANGE = 'OR'
    GREEN = 'GR'
    BLUE = 'BL'
    PURPLE = 'PL'
    BROWN = 'BR'
    RED = 'RD'
    BLACK = 'BK'
    BELT_RANK_CHOICES = (
        (WHITE, 'White'),
        (YELLOW, 'Yellow'),
        (ORANGE, 'Orange'),
        (GREEN, 'Green'),
        (BLUE, 'Blue'),
        (PURPLE, 'Purple'),
        (BROWN, 'Brown'),
        (RED, 'Red'),
        (BLACK, 'Black'),
    )

    BELT_RANK_LABELS = dict(BELT_RANK_CHOICES)
    BELT_RANK_VALUES = {v.lower():k for k,v in BELT_RANK_LABELS.items()}

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 2
        kwargs['choices'] = BeltRankField.BELT_RANK_CHOICES
        return super().__init__(*args, **kwargs)

    def to_python(self, value):
        if not value in BeltRankField.BELT_RANK_LABELS:
            raise(ValidationError("Invalid BeltRankField value: "
                    + value))
        return value

    @staticmethod
    def label(l):
        return BeltRankField.BELT_RANK_LABELS[l]

    @staticmethod
    def value(v):
        return BeltRankField.BELT_RANK_VALUES[v.lower()]

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
        self.slug = self.slugify()
        new_tournament = not self.id

        super(Tournament, self).save(*args, **kwargs)

        if new_tournament:
            self.create_divisions()

    def slugify(self):
        return slugify(self.location) + '-' + slugify(self.date)

    def create_divisions(self):
        sex_labels = SexField.SEX_LABELS
        skill_labels = DivisionLevelField.DIVISION_LEVEL_LABELS
        for sex, skill_level in product(sex_labels, skill_labels):
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
        self.slug = self.slugify()
        new_school = not self.id

        super(School, self).save(*args, **kwargs)

        if new_school:
            self.create_teams()

    def create_teams(self):
        sex_labels = SexField.SEX_LABELS
        skill_labels = DivisionLevelField.DIVISION_LEVEL_LABELS
        for sex, skill_level in product(sex_labels, skill_labels):
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
                roster = [r.strip() for r in roster]
                team = Team.objects.get_or_create(school=self.school,
                        division=division, number=team_num+1)[0]
                tournament_division = TournamentDivision.objects.get(
                        tournament=self.tournament, division=division)
                team_reg = TeamRegistration.objects.get_or_create(
                        tournament_division=tournament_division, team=team)[0]
                self.save_team_roster(team_reg, roster, competitors)

    def drop_competitors_and_teams(self, force=False):
        if not self.imported and not force:
            raise IntegrityError(("%s is not imported" %(self)
                    + " - and must be imported before it is dropped"))

        TeamRegistration.objects.filter(
                tournament_division__tournament=self.tournament,
                team__school=self.school).delete()
        Competitor.objects.filter(registration=self).delete()
        self.imported = False
        self.save()

    def import_competitors_and_teams(self, reimport=False):
        if self.imported and not reimport:
            raise IntegrityError(("%s is already imported" %(self.school)
                    + " and will not be reimported"))

        self.drop_competitors_and_teams(force=True)
        school_extracted_data = self.download_school_registration()
        self.validate_school_extracted_data(school_extracted_data)
        competitors = self.save_extracted_competitors(
                school_extracted_data.extracted_competitors)
        self.save_extracted_teams(school_extracted_data.teams, competitors)
        self.imported = True
        self.save()

    def validate_school_extracted_data(self, extracted_data):
        SchoolRegistrationError.objects.filter(
                school_registration=self).delete()
        errors = SchoolRegistrationValidator(self, extracted_data).validate()
        if not errors:
            return
        for error in errors:
            error.save()
        raise SchoolValidationError("There are errors in %s's registration spreadsheet - correct the errors in their spreadsheet and reimport." %(self.school,))


class SchoolRegistrationError(models.Model):
    school_registration = models.ForeignKey(SchoolRegistration)
    error_text = models.TextField()

class Division(models.Model):
    sex = SexField()
    skill_level = DivisionLevelField()
    slug = models.SlugField(unique=True)
    tournaments = models.ManyToManyField('Tournament',
            through='TournamentDivision')

    class Meta:
        unique_together = (("sex", "skill_level"),)

    def save(self, *args, **kwargs):
        self.slug = self.slugify()
        super(Division, self).save(*args, **kwargs)

    def slugify(self):
        return slugify(str(self))

    def __str__(self):
        if self.sex == SexField.FEMALE: sex_name = "Women's"
        if self.sex == SexField.MALE: sex_name = "Men's"
        return sex_name + " " + self.skill_level

    def match_number_start_val(self):
        if self.skill_level == DivisionLevelField.A_TEAM_VAL:
            start_val = 100
        elif self.skill_level == DivisionLevelField.B_TEAM_VAL:
            start_val = 300
        elif self.skill_level == DivisionLevelField.C_TEAM_VAL:
            start_val = 500
        return start_val + (100 if self.sex == SexField.FEMALE else 0) + 1

class TournamentDivisionStatus():
    def __init__(self, num_matches, num_matches_completed):
        self.num_matches = num_matches
        self.num_matches_completed = num_matches_completed

    def __str__(self):
        if not self.num_matches:
            return "No matches created"
        return "%d/%d matches completed" %(
                 self.num_matches_completed, self.num_matches,)

class TournamentDivision(models.Model):
    tournament = models.ForeignKey(Tournament)
    division = models.ForeignKey(Division)

    class Meta:
        unique_together = (('tournament', 'division'),)

    def __str__(self):
        return "%s" %(self.division)

    def __repr__(self):
        return "%s (%s)" %(self.division, self.tournament)

    def status(self):
        matches = TeamMatch.objects.filter(division=self)
        num_matches = num_matches_completed = 0
        for match in matches:
            num_matches += 1
            num_matches_completed += bool(match.winning_team)
        return TournamentDivisionStatus(num_matches, num_matches_completed)

    def assign_slots_to_team_registrations(self):
        """
        Assigns all teams in tournament_division to a slot in the
        bracket.
        """
        teams = TeamRegistration.objects.filter(tournament_division=self)
        teams = teams.order_by('team__number').order_by('team__school')
        teams = list(teams)
        slot_assigner = SlotAssigner(list(teams), 4,
                get_school_name = lambda team: team.team.school.name,
                get_points = lambda team: team.points if team.points else 0)
        with transaction.atomic():
            for team in teams:
                team.seed = None
                team.save()
            for team in teams:
                team.seed = slot_assigner.slots_by_team.get(team)
                team.save()
        return teams

    def create_matches_from_slots(self):
        TeamMatch.objects.filter(division=self).delete()
        seeded_teams = TeamRegistration.objects.filter(
                tournament_division=self, seed__isnull=False)
        seeds = {team.seed:team for team in seeded_teams}
        start_val = self.division.match_number_start_val()
        bracket = BracketGenerator(seeds, match_number_start_val=start_val)
        for bracket_match in bracket:
            match = TeamMatch(division=self,
                    number=bracket_match.number,
                    round_num = bracket_match.round_num,
                    round_slot = bracket_match.round_slot)

            try:
                match.blue_team = bracket_match.blue_team
            except AttributeError:
                pass
            try:
                bracket_match.red_team
            except: pass
            try:
                match.red_team = bracket_match.red_team
            except AttributeError:
                pass

            match.clean()
            match.save()

class TournamentDivisionBeltRanks(models.Model):
    belt_rank = BeltRankField()
    tournament_division = models.ForeignKey(TournamentDivision)

class Competitor(models.Model):
    """ A person who may compete in a tournament. """
    name = models.CharField(max_length=127)
    sex = SexField()
    belt_rank = BeltRankField()
    weight = WeightField(null=True, blank=True)
    registration = models.ForeignKey(SchoolRegistration)

    def belt_rank_label(self):
        return BeltRankField.label(self.belt_rank)

    def sex_label(self):
        return SexField.label(self.sex)

    def __str__(self):
        return "%s (%s)" % (self.name, self.registration.school)

    class Meta:
        unique_together = (("name", "registration"),)

class Team(models.Model):
    school = models.ForeignKey(School)
    division = models.ForeignKey(Division)
    number = models.SmallIntegerField()
    slug = models.SlugField(unique=True)
    registrations = models.ManyToManyField(TournamentDivision,
            through="TeamRegistration")

    def save(self, *args, **kwargs):
        self.slug = self.slugify()
        super(Team, self).save(*args, **kwargs)

    def slugify(self):
        return self.school.slug + '-' + self.division.slug + str(self.number)

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
            related_name="lightweight", on_delete=models.deletion.SET_NULL)
    middleweight = models.ForeignKey(Competitor, null=True, blank=True,
            related_name="middleweight", on_delete=models.deletion.SET_NULL)
    heavyweight = models.ForeignKey(Competitor, null=True, blank=True,
            related_name="heavyweight", on_delete=models.deletion.SET_NULL)
    alternate1 = models.ForeignKey(Competitor, null=True, blank=True,
            related_name="alternate1", on_delete=models.deletion.SET_NULL)
    alternate2 = models.ForeignKey(Competitor, null=True, blank=True,
            related_name="alternate2", on_delete=models.deletion.SET_NULL)

    class Meta:
        unique_together = (('tournament_division', 'team'),
                ('tournament_division', 'seed'),)

    def get_team_composition(self):
        lightweight = "L" if self.lightweight else ""
        middleweight = "M" if self.middleweight else ""
        heavyweight = "H" if self.heavyweight else ""
        if not lightweight and not middleweight and not heavyweight:
            return ""
        return lightweight + middleweight + heavyweight

    def __get_competitors_str(self):
        return "(" + self.get_team_composition() + ")"

    def get_competitors_ids(self):
        competitors = []
        if self.lightweight:
            competitors.append(self.lightweight.id)
        if self.middleweight:
            competitors.append(self.middleweight.id)
        if self.heavyweight:
            competitors.append(self.heavyweight.id)
        return competitors

    def __str__(self):
        competitors_str = self.__get_competitors_str()
        if competitors_str:
            competitors_str = " " + competitors_str
        return "%s%s" %(str(self.team), competitors_str)

    def __repr__(self):
        return "%s (%s)" %(str(self.team),
                str(self.tournament_division.tournament),)

    def bracket_str(self):
        team_str = "%s %s%d %s" %(self.team.school,
                self.team.division.skill_level,
                self.team.number,
                self.__get_competitors_str())
        if self.seed:
            team_str = "[%d] %s" %(self.seed, team_str)
        return team_str

    def num_competitors(self):
        return sum(map(lambda x: x is not None,
                [self.lightweight, self.middleweight, self.heavyweight]))

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

    @staticmethod
    def order_queryset(query_set):
        return query_set.order_by('team__school__name',
                'tournament_division__division', 'team__number')

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
    in_holding = models.BooleanField(default=False)
    at_ring = models.BooleanField(default=False)
    competing = models.BooleanField(default=False)

    class Meta:
        unique_together = (
                ("division", "round_num", "round_slot"),
                ("division", "number",),
        )

    def __str__(self):
        return "Match #" + str(self.number)

    def status(self):
        if self.winning_team:
                return "Complete"
        elif self.competing:
                return 'Competing'
        elif self.ring_number:
                return "At ring " + str(self.ring_number)
        elif self.in_holding:
                return "Report to holding"
        return "----"

    def round_str(self):
        if self.round_num == 0:
            return "Finals"
        if self.round_num == 1:
            return "Semi-Finals"
        if self.round_num == 2:
            return "Quarter-Finals"
        return "Round of %d" %(1 << (self.round_num))

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

    @staticmethod
    def get_matches_by_round(tournament_division):
        matches = {}
        num_rounds = 0
        for match in TeamMatch.objects.filter(division=tournament_division):
            matches[(match.round_num, match.round_slot)] = match
            num_rounds = max(num_rounds, match.round_num)
        return matches, num_rounds

    def update_winning_team(self):
        parent_match = self.get_next_round_match()
        if not parent_match:
            return
        if parent_match.winning_team:
            raise IntegrityError("Unable to update match - match #%d's winning team must be removed first" %(parent_match.number))
        if self.round_slot % 2:
            if parent_match.red_team == self.winning_team:
                return
            parent_match.red_team = self.winning_team
        else:
            if parent_match.blue_team == self.winning_team:
                return
            parent_match.blue_team = self.winning_team
        parent_match.clean()
        parent_match.save()

    def clean(self, *args, **kwargs):
        self.update_winning_team()

class ConfigurationSetting(models.Model):
    key = models.TextField(unique=True)
    value = models.TextField()
    REGISTRATION_CREDENTIALS = 'registration_credentials'

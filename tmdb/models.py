from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from itertools import product
from django.template.defaultfilters import slugify

from tmdb.util import BracketGenerator, SlotAssigner, parse_team_file
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

class SparringDivisionLevelField(models.CharField):
    A_TEAM_VAL = 'A'
    B_TEAM_VAL = 'B'
    C_TEAM_VAL = 'C'
    POOMSAE_TEAM_VAL = 'P'
    DIVISION_LEVEL_CHOICES = (
        (A_TEAM_VAL, 'A-team'),
        (B_TEAM_VAL, 'B-team'),
        (C_TEAM_VAL, 'C-team'),
        (POOMSAE_TEAM_VAL, 'Poomsae-team'),
    )

    DIVISION_LEVEL_LABELS = dict(DIVISION_LEVEL_CHOICES)
    DIVISION_LEVEL_VALUES = {v.lower():k for k,v in DIVISION_LEVEL_LABELS.items()}

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 1
        kwargs['choices'] = SparringDivisionLevelField.DIVISION_LEVEL_CHOICES
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if not value in SparringDivisionLevelField.DIVISION_LEVEL_LABELS:
            raise(ValidationError("Invalid SparringDivisionLevelField value: "
                    + value))
        return value

    @staticmethod
    def label(l):
        return SparringDivisionLevelField.DIVISION_LEVEL_LABELS[l]

    @staticmethod
    def value(v):
        return SparringDivisionLevelField.DIVISION_LEVEL_VALUES[v.lower()]

DivisionLevelField = SparringDivisionLevelField

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

class Season(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    slug = models.SlugField(unique=True)
    schools = models.ManyToManyField('School',
            through='SchoolSeasonRegistration')

    def validate_start_end_date(self):
        if self.end_date > self.start_date:
            return
        return ValidationError(
                "End date [%s] cannot be before start date [%s]" %(
                        str(self.end_date), str(self.start_date)))

    def validate_unique_start_year(self):
        existing = Season.objects.filter(
                start_date__year=self.start_date.year).exclude(
                id=self.id).first()
        if existing:
            return ValidationError("A season already exists starting in %d" %(
                    self.start_date.year))

    def clean(self, *args, **kwargs):
        errors = []

        error = self.validate_start_end_date()
        if error: errors.append(error)
        error = self.validate_unique_start_year()
        if error: errors.append(error)

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.end_date is None:
            self.end_date = self.start_date.replace(year=self.start_date.year+1)
        self.slug = self.slugify()
        self.full_clean()
        return super(Season, self).save(*args, **kwargs)

    def slugify(self):
        return "%d-%d" %(self.start_date.year, self.end_date.year)

    def __str__(self):
        return "%d-%d Season" %(self.start_date.year, self.end_date.year)

    def tournaments(self):
        return Tournament.objects.filter(season=self)

class Tournament(models.Model):
    slug = models.SlugField(unique=True)
    season = models.ForeignKey(Season, on_delete=models.PROTECT)
    location = models.CharField(max_length=127)
    date = models.DateField()
    registration_doc_url = models.URLField(unique=True)
    imported = models.BooleanField(default=False)

    def validate_season(self):
        if self.season.start_date < self.date < self.season.end_date:
            return
        return ValidationError(
                "Tournament date [%s] must be between season dates [%s, %s]" %(
                        self.date,
                        self.season.start_date,
                        self.season.end_date,))

    def clean(self, *args, **kwargs):
        errors = []

        error = self.validate_season()
        if error: errors.append(error)

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.slug = self.slugify()
        self.full_clean()
        new_tournament = not self.id

        super(Tournament, self).save(*args, **kwargs)

        if new_tournament:
            self.create_divisions()

    def slugify(self):
        return slugify(self.location) + '-' + slugify(self.date)

    def create_divisions(self):
        sex_labels = SexField.SEX_LABELS
        skill_labels = SparringDivisionLevelField.DIVISION_LEVEL_LABELS
        for sex, skill_level in product(sex_labels, skill_labels):
            division = SparringDivision.objects.get_or_create(
                    sex=sex, skill_level=skill_level)[0]
            TournamentSparringDivision.objects.get_or_create(
                    tournament=self, division=division)[0]

    def __str__(self):
        return "%s Tournament (%s)" %(
                self.location, self.date.strftime("%Y %b %d"))

    def __repr__(self):
        return self.slug if self.slug else self.slugify()

    def import_school_registrations(self, team_file):
        SparringTeamRegistration.objects.filter(
                tournament_division__tournament=self).delete()
        teams = parse_team_file(team_file)
        for division, teams in teams.items():
            for team in teams:
                self.import_team(team)

    def import_team(self, team):
        school = School.objects.get_or_create(name=team['school_name'])[0]
        school_season_registration = SchoolSeasonRegistration.objects.get_or_create(
                school=school, season=self.season, defaults={'division': 3})[0]
        school_tournament_registration = SchoolTournamentRegistration.objects.get_or_create(
                tournament=self,
                school_season_registration=school_season_registration,
                registration_doc_url = None,
                imported=True)[0]
        sparring_team = SparringTeam.objects.get_or_create(school=school,
                division=team['sparring_division'],
                number=team['team_num'])[0]
        tournament_division = TournamentSparringDivision.objects.get_or_create(
                tournament=self, division=team['sparring_division'])[0]
        sparring_team_registration = SparringTeamRegistration(
                tournament_division=tournament_division,
                lightweight=team['has_lightweight'],
                middleweight=team['has_middleweight'],
                heavyweight=team['has_heavyweight'],
                team=sparring_team)
        sparring_team_registration.save()
        return sparring_team_registration

class School(models.Model):
    name = models.CharField(max_length=127, unique=True)
    slug = models.SlugField(unique=True)
    seasons = models.ManyToManyField('Season',
            through='SchoolSeasonRegistration')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.slugify()
        super(School, self).save(*args, **kwargs)

    def create_division_teams(self, division):
        for team_num in range(1,11):
            team = SparringTeam(school=self, division=division,
                    number=team_num)
            team.clean()
            team.save()

    def slugify(self):
        return slugify(self.name)

    def __str__(self):
        return self.name

class SchoolSeasonRegistration(models.Model):
    school = models.ForeignKey(School, on_delete=models.PROTECT)
    season = models.ForeignKey(Season, on_delete=models.PROTECT)
    division = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = (('season', 'school'),)

    def __str__(self):
        return "%s %s (Div. #%d)" %(str(self.school), str(self.season),
                self.division)

class SchoolTournamentRegistration(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    school_season_registration = models.ForeignKey(SchoolSeasonRegistration, on_delete=models.PROTECT)
    registration_doc_url = models.URLField(null=True, blank=True, unique=False)
    imported = models.BooleanField(default=False)

    class Meta:
        unique_together = (('tournament', 'school_season_registration'),)

    def __str__(self):
        return '%s at %s' %(self.school_season_registration.school,
                self.tournament)

    def drop_competitors_and_teams(self, force=False):
        SparringTeamRegistration.objects.filter(
                tournament_division__tournament=self.tournament,
                team__school=self.school_season_registration.school).delete()
        self.imported = False
        self.save()

class SchoolTournamentRegistrationError(models.Model):
    school_registration = models.ForeignKey(SchoolTournamentRegistration, on_delete=models.CASCADE)
    error_text = models.TextField()

class SparringDivision(models.Model):
    sex = SexField()
    skill_level = SparringDivisionLevelField()
    slug = models.SlugField(unique=True)
    tournaments = models.ManyToManyField('Tournament',
            through='TournamentSparringDivision')

    class Meta:
        unique_together = (("sex", "skill_level"),)

    def save(self, *args, **kwargs):
        self.slug = self.slugify()
        self.full_clean()
        super(SparringDivision, self).save(*args, **kwargs)

    def slugify(self):
        return slugify(str(self))

    def __str__(self):
        if self.sex == SexField.FEMALE: sex_name = "Women's"
        if self.sex == SexField.MALE: sex_name = "Men's"
        return sex_name + " " + self.skill_level

    def match_number_start_val(self):
        if self.skill_level == SparringDivisionLevelField.A_TEAM_VAL:
            start_val = 100
        elif self.skill_level == SparringDivisionLevelField.B_TEAM_VAL:
            start_val = 300
        elif self.skill_level == SparringDivisionLevelField.C_TEAM_VAL:
            start_val = 500
        return start_val + (100 if self.sex == SexField.FEMALE else 0) + 1

class TournamentSparringDivisionStatus():
    def __init__(self, num_matches, num_matches_completed):
        self.num_matches = num_matches
        self.num_matches_completed = num_matches_completed

    def __str__(self):
        if not self.num_matches:
            return "No matches created"
        return "%d/%d matches completed" %(
                 self.num_matches_completed, self.num_matches,)

class TournamentSparringDivision(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    division = models.ForeignKey(SparringDivision, on_delete=models.PROTECT)

    class Meta:
        unique_together = (('tournament', 'division'),)

    def __str__(self):
        return "%s" %(self.division)

    def __repr__(self):
        return "%s (%s)" %(self.division, self.tournament)

    def status(self):
        matches = SparringTeamMatch.objects.filter(division=self)
        num_matches = num_matches_completed = 0
        for match in matches:
            num_matches += 1
            num_matches_completed += bool(match.winning_team)
        return TournamentSparringDivisionStatus(num_matches,
                num_matches_completed)

    def assign_slots_to_team_registrations(self):
        """
        Assigns all teams in tournament_division to a slot in the
        bracket.
        """
        teams = SparringTeamRegistration.objects.filter(
                tournament_division=self)
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
        SparringTeamMatch.objects.filter(division=self).delete()
        seeded_teams = SparringTeamRegistration.objects.filter(
                tournament_division=self, seed__isnull=False)
        seeds = {team.seed:team for team in seeded_teams}
        start_val = self.division.match_number_start_val()
        bracket = BracketGenerator(seeds, match_number_start_val=start_val)
        for bracket_match in bracket:
            match = SparringTeamMatch(division=self,
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

class TournamentSparringDivisionBeltRanks(models.Model):
    belt_rank = BeltRankField()
    tournament_division = models.ForeignKey(TournamentSparringDivision, on_delete=models.CASCADE)

class SparringTeam(models.Model):
    school = models.ForeignKey(School, on_delete=models.PROTECT)
    division = models.ForeignKey(SparringDivision, on_delete=models.PROTECT)
    number = models.SmallIntegerField()
    slug = models.SlugField(unique=True)
    registrations = models.ManyToManyField(TournamentSparringDivision,
            through="SparringTeamRegistration")

    def save(self, *args, **kwargs):
        self.slug = self.slugify()
        super(SparringTeam, self).save(*args, **kwargs)

    def slugify(self):
        return self.school.slug + '-' + self.division.slug + str(self.number)

    class Meta:
        unique_together = (('school', 'division', 'number',),)

    def __str__(self):
        return "%s %s%d" %(str(self.school), str(self.division), self.number,)

#TODO team.division must equal tournament_division.division
class SparringTeamRegistration(models.Model):
    tournament_division = models.ForeignKey(TournamentSparringDivision, on_delete=models.CASCADE)
    team = models.ForeignKey(SparringTeam, on_delete=models.PROTECT)
    seed = models.PositiveSmallIntegerField(null=True, blank=True)
    points = models.PositiveIntegerField(null=True, blank=True)
    lightweight = models.BooleanField(default=False)
    middleweight = models.BooleanField(default=False)
    heavyweight = models.BooleanField(default=False)
    alternate1 = models.BooleanField(default=False)
    alternate2 = models.BooleanField(default=False)

    class Meta:
        unique_together = (('tournament_division', 'team'),
                ('tournament_division', 'seed'),)

    def get_team_composition(self):
        composition = ""
        if self.lightweight:
            composition += "L"
        if self.middleweight:
            composition += "M"
        if self.heavyweight:
            composition += "H"
        alternate_str = ""
        if self.alternate1:
            alternate_str += "A"
        if self.alternate2:
            alternate_str += "A"
        if alternate_str:
            composition = "%s-%s" %(composition, alternate_str)
        return composition

    def __get_competitors_str(self):
        return "(" + self.get_team_composition() + ")"

    def __str__(self):
        competitors_str = self.__get_competitors_str()
        if competitors_str:
            competitors_str = " " + competitors_str
        return "%s%s" %(str(self.team), competitors_str)

    def __repr__(self):
        return "%s (%s)" %(str(self.team),
                str(self.tournament_division.tournament),)

    def team_list_str(self):
        return str(self)

    def bracket_str(self):
        team_str = "%s %s%d %s" %(self.team.school,
                self.team.division.skill_level,
                self.team.number,
                self.__get_competitors_str())
        if self.seed:
            team_str = "[%d] %s" %(self.seed, team_str)
        return team_str

    def num_competitors(self):
        return sum(map(lambda x: bool(x),
                [self.lightweight, self.middleweight, self.heavyweight]))

    @classmethod
    def get_teams_without_assigned_slot(cls, tournament_division):
        """
        Returns a list of teams that do not have a slot in the bracket.

        Currently, the condition for this is SparringTeamRegistration.seed is
        empty.
        """
        return cls.objects.filter(
                tournament_division=tournament_division, seed__isnull=True) \
                .order_by('team__school__name', 'team__number')

    @staticmethod
    def order_queryset(query_set):
        return query_set.order_by('team__school__name',
                'tournament_division__division', 'team__number')

class SparringTeamMatch(models.Model):
    """A match between two SparringTeams in a SparringDivision.

    Attributes:
        division        The TournamentSparringDivision that the match is being
                        fought in
        number          The match number (unique amongst all
                        SparringTeamMatches)
        round_num       Which round is this match in terms of distance
                        from the final? (0 means this match is the
                        final, 1 means this match is the semi-final,
                        etc.). The number of matches in a given round is
                        (2**round_num)
        round_slot      Which slot (from top to bottom) does this match
                        belong to in its round? 0 means top of the
                        bracket, 1 = second from the top of the round,
                        and (2**round_num - 1) = bottom of the round.
        blue_team       The SparringTeam fighting in blue for this match
        red_team        The SparringTeam fighting in red for this match
        ring_number     The number of the assigned ring
        ring_assignment_time
                        The time at which the ring was assigned
        winning_team    The winner of the SparringTeamMatch
    """
    division = models.ForeignKey(TournamentSparringDivision, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    round_num = models.SmallIntegerField()
    round_slot = models.IntegerField()
    blue_team = models.ForeignKey(SparringTeamRegistration,
            related_name="blue_team", blank=True, null=True,
            on_delete=models.SET_NULL)
    red_team = models.ForeignKey(SparringTeamRegistration,
            related_name="red_team", blank=True, null=True,
            on_delete=models.SET_NULL)
    ring_number = models.PositiveIntegerField(blank=True, null=True)
    ring_assignment_time = models.DateTimeField(blank=True, null=True)
    winning_team = models.ForeignKey(SparringTeamRegistration, blank=True,
            null=True, related_name="winning_team", on_delete=models.PROTECT)
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
        upper_match_query = SparringTeamMatch.objects.filter(
                division=self.division, round_num=self.round_num + 1,
                round_slot=2*self.round_slot)
        lower_match_query = SparringTeamMatch.objects.filter(
                division=self.division, round_num=self.round_num + 1,
                round_slot=2*self.round_slot + 1)
        return [upper_match_query.first(), lower_match_query.first()]

    def get_next_round_match(self):
        try:
            return SparringTeamMatch.objects.get(division=self.division,
                    round_num=self.round_num-1,
                    round_slot = self.round_slot / 2)
        except SparringTeamMatch.DoesNotExist:
            return None

    @staticmethod
    def get_matches_by_round(tournament_division):
        matches = {}
        num_rounds = 0
        for match in SparringTeamMatch.objects.filter(
                division=tournament_division):
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

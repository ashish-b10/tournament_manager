from django.db import models
from django.core.exceptions import ValidationError
import decimal
from itertools import product
from django.template.defaultfilters import slugify

from tmdb.util import Bracket

class SexField(models.CharField):
    FEMALE_DB_VAL = 'F'
    MALE_DB_VAL = 'M'
    choices = (
        (FEMALE_DB_VAL, 'Female'),
        (MALE_DB_VAL, 'Male'),
    )
    _sexes_names = dict(choices)

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 1
        super(SexField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value in SexField._sexes_names.keys():
            raise ValidationError("Invalid SexField value: " + value)
        return value

    def __str__(self):
        return self._sexes_names[self.sex]

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

class BeltRank(models.Model):
    BELT_RANKS = (
        ('WH', 'White'),
        ('YL', 'Yellow'),
        ('OR', 'Orange'),
        ('GN', 'Green'),
        ('BL', 'Blue'),
        ('PL', 'Purple'),
        ('BR', 'Brown'),
        ('RD', 'Red'),
        ('BK', 'Black'),
        ('1D', '1 Dan'),
        ('2D', '2 Dan'),
        ('3D', '3 Dan'),
        ('4D', '4 Dan'),
        ('5D', '5 Dan'),
        ('6D', '6 Dan'),
        ('7D', '7 Dan'),
        ('8D', '8 Dan'),
        ('9D', '9 Dan'),
    )
    _belt_ranks_names = dict(BELT_RANKS)
    _belt_ranks_set = {rank[0] for rank in BELT_RANKS}

    belt_rank = models.CharField(max_length=2, choices=BELT_RANKS, unique=True)

    def save(self, *args, **kwargs):
        if not self.belt_rank in BeltRank._belt_ranks_set:
            raise ValidationError("Invalid BeltRank value: "
                    + str(self.belt_rank))
        super().save(*args, **kwargs)

    def __str__(self):
        return self._belt_ranks_names[self.belt_rank]

    @staticmethod
    def create_tkd_belt_ranks():
        for belt_rank in BeltRank._belt_ranks_set:
            BeltRank.objects.create(belt_rank = belt_rank)

class WeightField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 4
        kwargs['decimal_places'] = 1
        super(WeightField, self).__init__(*args, **kwargs)

class Tournament(models.Model):
    slug = models.SlugField(unique=True)
    location = models.CharField(max_length=63)
    date = models.DateField()
    registration_doc_url = models.URLField(unique=True)
    imported = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = self.slugify()

        super(Tournament, self).save(*args, **kwargs)

    def slugify(self):
        return slugify(self.location) + '-' + slugify(self.date)

    def __str__(self):
        return self.slug if self.slug else self.slugify()

    def download_registration(self):
        """Downloads registration spreadsheet from registration_doc_url."""
        from ectc_registration import GoogleDocsDownloader
        from ectc_registration import RegistrationExtractor
        try:
            creds = ConfigurationSetting.objects.get(
                    key=ConfigurationSetting.REGISTRATION_CREDENTIALS).value
        except tmdb.models.DoesNotExist:
            raise IntegrityError("Registration credentials have not been"
                    + " provided")
        downloader = GoogleDocsDownloader(creds)
        reg_extractor = RegistrationExtractor(self.registration_doc_url,
                downloader)
        return reg_extractor.get_registration_workbooks()

    def save_downloaded_school(self, school):
        school_object = Organization.objects.filter(
                name=school.school_name).first()
        if school_object is None:
            school_object = Organization(name=school.school_name)
            school_object.clean()
            school_object.save()
        registration = TournamentOrganization(tournament=self,
                organization=school_object,
                registration_doc_url=school.registration_doc_feed_url)
        registration.clean()
        registration.save()

    def save_downloaded_schools(self, schools):
        for school in schools:
            self.save_downloaded_school(school)

    def import_tournament_organizations(self):
        """Imports organizations from registration_doc_url."""
        if self.imported:
            raise ValidationError(("%s is already imported - to reimport,"
                    + " unimport first, then run import again") %self)
        registered_schools = self.download_registration()
        self.save_downloaded_schools(registered_schools)

        self.imported = True
        self.save()

class Organization(models.Model):
    name = models.CharField(max_length=31, unique=True)
    tournaments = models.ManyToManyField('Tournament',
            through='TournamentOrganization')

    def __str__(self):
        return self.name

class TournamentOrganization(models.Model):
    tournament = models.ForeignKey(Tournament)
    organization = models.ForeignKey(Organization)
    registration_doc_url = models.URLField(unique=True)
    imported = models.BooleanField(default=False)

    class Meta:
        unique_together = (('tournament', 'organization'),)

    def __str__(self):
        return '%s/%s' %(self.tournament, self.organization,)

class Division(models.Model):
    belt_ranks = models.ManyToManyField(BeltRank)
    sex = SexField()
    skill_level = DivisionSkillField()

    class Meta:
        unique_together = (("sex", "skill_level"),)

    def __str__(self):
        if self.sex == SexField.MALE_DB_VAL: sex_name = "Men's"
        if self.sex == SexField.FEMALE_DB_VAL: sex_name = "Women's"
        return sex_name + ' ' + self.skill_level

    def match_num_start_val(self):
        if self.skill_level == DivisionSkillField.A_TEAM_VAL:
            match_num = 100
        if self.skill_level == DivisionSkillField.B_TEAM_VAL:
            match_num = 300
        if self.skill_level == DivisionSkillField.B_TEAM_VAL:
            match_num = 500
        if self.sex == SexField.FEMALE_DB_VAL:
            match_num += 100
        return match_num

    c_team_belt_ranks = ("WH", "YL", "OR", "GN")
    b_team_belt_ranks = ("GN", "BL", "PL", "BR", "RD")
    a_team_belt_ranks = ("BL", "PL", "BR", "RD", "BK", "1D", "2D", "3D", "4D",
            "5D", "6D", "7D", "8D", "9D",)
    DIVISION_SEX_NAMES = {"F" : "Women's", "M" : "Men's"}
    ECTC_DIVISION_SKILLS = {"A" : a_team_belt_ranks, "B" : b_team_belt_ranks,
            "C" : c_team_belt_ranks}

    @staticmethod
    def get_match_number_start_val(division):
        division = Division.objects.get(division)

    def _validate_sex(self, competitor):
        if self.sex == competitor.sex: return
        raise ValidationError(("Competitor %s cannot be added to Division %s"
                + " (invalid sex)") %(str(competitor), str(self)))

    def _validate_belt_group(self, competitor):
        if competitor.skill_level in self.belt_ranks.all():
            return
        raise ValidationError(("Competitor %s's belt rank is invalid for"
                + " division %s") %(str(competitor), str(self)))

    def validate_competitor(self, competitor):
        if competitor is None: return
        self._validate_sex(competitor)
        self._validate_belt_group(competitor)

    @staticmethod
    def get_match_num_start_val(sex, skill):
        if sex == "M" and skill == "A": return 100
        if sex == "F" and skill == "A": return 200
        if sex == "M" and skill == "B": return 300
        if sex == "F" and skill == "B": return 400
        if sex == "M" and skill == "C": return 500
        if sex == "F" and skill == "C": return 600

    @classmethod
    def create_ectc_divisions(self):
        for sex, skill_name in product(("F", "M"),
                Division.ECTC_DIVISION_SKILLS):
            belt_ranks = Division.ECTC_DIVISION_SKILLS[skill_name]
            division = Division.objects.create(sex=sex, skill_level=skill_name)
            division.belt_ranks.add(*BeltRank.objects.filter(
                    belt_rank__in=belt_ranks))

class Competitor(models.Model):
    """ Cutoff weights for each weight class in pounds inclusive. """
    WEIGHT_CUTOFFS = {
        'F' : {
            'light': (decimal.Decimal('0'), decimal.Decimal('117.0')),
            'middle': (decimal.Decimal('117.1'), decimal.Decimal('137.0')),
            'heavy': (decimal.Decimal('137.1'), decimal.Decimal('999.9')),
        },
        'M' : {
            'light': (decimal.Decimal('0'), decimal.Decimal('145.0')),
            'middle': (decimal.Decimal('145.1'), decimal.Decimal('172.0')),
            'heavy': (decimal.Decimal('172.1'), decimal.Decimal('999.9')),
        },
    }
    name = models.CharField(max_length=63)
    sex = SexField()
    skill_level = models.ForeignKey(BeltRank)
    age = models.IntegerField()
    organization = models.ForeignKey(Organization)
    weight = WeightField()
    class Meta:
        unique_together = (("name", "organization"),)

    @staticmethod
    def _is_between_cutoffs(weight, sex, weightclass):
        cutoffs = Competitor.WEIGHT_CUTOFFS[sex][weightclass]
        return weight >= cutoffs[0] and weight <= cutoffs[1]

    def is_lightweight(self):
        return self._is_between_cutoffs(self.weight, self.sex, 'light')

    def is_middleweight(self):
        return self._is_between_cutoffs(self.weight, self.sex, 'middle')

    def is_heavyweight(self):
        return self._is_between_cutoffs(self.weight, self.sex, 'heavy')

    def __str__(self):
        return "%s (%s)" % (self.name, self.organization)

class Team(models.Model):
    number = models.IntegerField()
    division = models.ForeignKey(Division)
    organization = models.ForeignKey(Organization)
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
    seed = models.IntegerField(null=True, blank=True)
    class Meta:
        unique_together = (("number", "division", "organization"),
                ("seed", "division"))

    def _valid_member_organization(self, member):
        if member is None: return True
        return self.organization == member.organization

    def _validate_member_organizations(self):
        if not self._valid_member_organization(self.lightweight):
            raise ValidationError(("Lightweight [%s] is not from same" +
                    " organization as [%s]") %(self.lightweight, self))
        if not self._valid_member_organization(self.middleweight):
            raise ValidationError(("Middleweight [%s] is not from same" +
                    " organization as [%s]") %(self.lightweight, self))
        if not self._valid_member_organization(self.heavyweight):
            raise ValidationError(("Heavyweight [%s] is not from same" +
                    " organization as [%s]") %(self.lightweight, self))
        if not self._valid_member_organization(self.alternate1):
            raise ValidationError(("Alternate1 [%s] is not from same" +
                    " organization as [%s]") %(self.lightweight, self))
        if not self._valid_member_organization(self.alternate2):
            raise ValidationError(("Alternate2 [%s] is not from same" +
                    " organization as [%s]") %(self.lightweight, self))

    def _validate_lightweight_eligibility(self):
        if self.lightweight is None: return

        if not self.lightweight.is_lightweight():
            raise ValidationError(("Competitor %s has invalid weight for"
                    + " lightweight spot [%d lbs]")
                    %(self.lightweight, self.lightweight.weight))

    def _validate_middleweight_eligibility(self):
        if self.middleweight is None: return

        if self.middleweight.is_heavyweight():
            raise ValidationError(("Competitor %s has invalid weight for"
                    + " middleweight spot [%d lbs]")
                    %(self.middleweight, self.middleweight.weight))

    def _validate_heavyweight_eligibility(self):
        if self.heavyweight is None: return

        if self.heavyweight.is_lightweight():
            raise ValidationError(("Competitor %s has invalid weight for"
                    + " heavyweight spot [%d lbs]")
                    %(self.heavyweight, self.heavyweight.weight))

    def _get_competitor_teams(competitor, field_names=None):
        """
        Return all teams which have competitor in any of the field names. The
        returned list could possibly contain duplicates.
        """
        teams = []
        for field_name in field_names:
            teams += Team.objects.filter(**{field_name: competitor})
        return teams

    def _validate_team_members_unique(self):
        """ Ensure that no member has multiple spots on this team. """
        # get all members that are not none
        members = [m for m in [self.lightweight, self.middleweight,
                self.heavyweight, self.alternate1, self.alternate2] if m]
        if len(members) != len(set(members)):
            raise ValidationError(("Duplicates found in members for team %s:"
                    + " %s") %(str(self), str(members)))

    def _validate_competitors_on_multiple_teams(self):
        """
        Validate that lightweight, middleweight and heavyweight are only on one
        team. Validate that alternates are not in a lightweight, middleweight,
        or heavyweight spot on any team.
        """
        for competitor in [self.lightweight, self.middleweight,
                self.heavyweight]:
            if competitor is None: continue
            teams = set(Team._get_competitor_teams(competitor, ["lightweight",
                    "middleweight", "heavyweight", "alternate1",
                    "alternate2"]))
            if self.pk: teams.discard(self)
            if teams:
                raise ValidationError(("Cannot add %s to team %s: already on"
                        + " other team(s): [%s]") %(competitor, self, teams))
        for competitor in [self.alternate1, self.alternate2]:
            if competitor is None: continue
            teams = set(Team._get_competitor_teams(competitor, ["lightweight",
                    "middleweight", "heavyweight"]))
            if self.pk: teams.discard(self)
            if teams:
                raise ValidationError(("Cannot add %s to team %s: already on"
                        + " other team(s): [%s] as non-alternate")
                        %(competitor, self, teams))

    def validate_team_members(self):
        """
        Validates that members of a team obey all ECTC rules. It is expected
        that this check is run BEFORE the team is committed to the database.
        """
        self._validate_member_organizations()
        self._validate_lightweight_eligibility()
        self._validate_middleweight_eligibility()
        self._validate_heavyweight_eligibility()
        self._validate_team_members_unique()
        self._validate_competitors_on_multiple_teams()
        self.division.validate_competitor(self.lightweight)
        self.division.validate_competitor(self.middleweight)
        self.division.validate_competitor(self.heavyweight)
        self.division.validate_competitor(self.alternate1)
        self.division.validate_competitor(self.alternate2)

    def clean(self, *args, **kwargs):
        self.validate_team_members()

    def __str__(self):
        return "%s %s%i" %(self.organization, self.division, self.number)

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
        division        The division that the match belongs to
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
    division = models.ForeignKey(Division)
    number = models.PositiveIntegerField(unique=True)
    parent = models.ForeignKey('self', blank=True, null=True)
    parent_side = models.IntegerField()
    root_match = models.BooleanField()
    blue_team = models.ForeignKey(Team, related_name="blue_team", blank=True,
            null=True)
    red_team = models.ForeignKey(Team, related_name="red_team", blank=True,
            null=True)
    ring_number = models.PositiveIntegerField(blank=True, null=True)
    ring_assignment_time = models.DateTimeField(blank=True, null=True)
    winning_team = models.ForeignKey(Team, blank=True, null=True,
            related_name="winning_team")
    class Meta:
        unique_together = (("parent", "parent_side"),)

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
    def create_matches_from_seeds(division):
        TeamMatch.objects.filter(division=division).delete()
        seeded_teams = Team.objects.filter(division=division).filter(
                seed__isnull=False)
        seeds = {team.seed:team for team in seeded_teams}
        bracket = Bracket(seeds,
                match_number_start_val=division.match_num_start_val())
        for bracket_match in bracket.bfs(seeds=False):
            match = TeamMatch(division=division, number=bracket_match.number,
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

    def validate_as_root_match(self):
        """ Validate this match as the root match. If it's not the root
        match, perform no checks and return. """
        if not self.root_match: return
        self.validate_single_root_match()

    def validate_as_nonroot_match(self):
        """ Validate this match as a non-root match. If it's the root
        match, perform no checks and return. """
        if self.root_match: return
        if self.parent is None:
            raise ValidationError("Non-root match must have non-null parent")
        if self.parent_side not in {0, 1}:
            raise ValidationError("parent_side must be in {0, 1}")

    def validate_distinct_participants(self):
        """ Validate the blue_team != red_team. """
        if self.blue_team is None: return
        if self.red_team is None: return
        if self.blue_team == self.red_team:
            raise ValidationError("blue_team == red_team is not permitted")

    def validate_winning_team(self):
        if self.winning_team is None: return
        if self.winning_team != self.blue_team and \
                self.winning_team != self.red_team:
            raise ValidationError("winning_team is %s, must be either %s or %s"
                    %(self.winning_team, self.blue_team, self.red_team))

    def validate_parent_participant_available(self):
        if not self.parent:
            return
        if self.parent_side == 0:
            slot_team = self.parent.blue_team
        elif self.parent_side == 1:
            slot_team = self.parent.red_team
        else:
            raise ValueError("parent_side is %d, must be 0 or 1",
                    self.parent_side)
        if slot_team is None:
            return
        if slot_team == self.red_team or slot_team == self.blue_team:
            if self.parent_side == 0:
                self.parent.blue_team = None
            else:
                self.parent.red_team = None
            self.parent.clean()
            self.parent.save()
            return
        raise ValidationError(("Cannot create on this side of parent %s"
                + " (already has %s as %s)") %(self.parent, slot_team,
                "blue_team" if self.parent_side == 0 else "red_team"))

    def validate_team_match(self):
        self.validate_as_root_match()
        self.validate_as_nonroot_match()
        self.validate_distinct_participants()
        self.validate_winning_team()
        self.validate_parent_participant_available()
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

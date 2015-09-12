from django.test import TestCase
from tmdb.models import Organization, Competitor, SexField, BeltRank, Division
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from decimal import Decimal
import itertools as it

class DivisionTestCase(TestCase):
    def setUp(self):
        BeltRank.create_tkd_belt_ranks()
        self.org1 = Organization.objects.create(name="org1")
        self.division_with_constraints = Division.objects.create(
                name="constraint_division", min_age=20, max_age=30,
                min_weight=110, max_weight=120, sex=SexField.FEMALE_DB_VAL)
        self.division_with_constraints.belt_ranks.add(
                *BeltRank.objects.filter(belt_rank__in=["WH", "YL"]))
        self.division_without_constraints = Division.objects.create(
                name="no_constraint_division", sex=SexField.FEMALE_DB_VAL)
        self.division_without_constraints.belt_ranks.add(
                *BeltRank.objects.filter(belt_rank__in=["WH", "YL"]))

    def test_str(self):
        self.assertEqual("constraint_division",
                str(self.division_with_constraints))

    def test_duplicate_division_name(self):
        Division.objects.create(name="test division",
                sex=SexField.FEMALE_DB_VAL)
        try:
            Division.objects.create(name="test division",
                    sex=SexField.FEMALE_DB_VAL)
        except IntegrityError:
            pass
        else:
            self.fail("Creating divisions with same name should produce"
                    + " IntegrityError")

    def verify_division_belt_ranks(self, belt_ranks, expected_belt_rank_names):
        self.assertTrue(len(belt_ranks) == len(expected_belt_rank_names))
        belt_rank_names = {belt_rank.belt_rank for belt_rank in belt_ranks}
        self.assertTrue(belt_rank_names == set(expected_belt_rank_names))

    def test_ectc_division_belt_ranks(self):
        Division.create_ectc_divisions()
        division = Division.objects.get(name="Women's A",
                sex=SexField.FEMALE_DB_VAL)
        self.verify_division_belt_ranks(division.belt_ranks.all(),
                Division.a_team_belt_ranks)
        division = Division.objects.get(name="Women's B",
                sex=SexField.FEMALE_DB_VAL)
        self.verify_division_belt_ranks(division.belt_ranks.all(),
                Division.b_team_belt_ranks)
        division = Division.objects.get(name="Women's C",
                sex=SexField.FEMALE_DB_VAL)
        self.verify_division_belt_ranks(division.belt_ranks.all(),
                Division.c_team_belt_ranks)
        division = Division.objects.get(name="Men's A",
                sex=SexField.MALE_DB_VAL)
        self.verify_division_belt_ranks(division.belt_ranks.all(),
                Division.a_team_belt_ranks)
        division = Division.objects.get(name="Men's B",
                sex=SexField.MALE_DB_VAL)
        self.verify_division_belt_ranks(division.belt_ranks.all(),
                Division.b_team_belt_ranks)
        division = Division.objects.get(name="Men's C",
                sex=SexField.MALE_DB_VAL)
        self.verify_division_belt_ranks(division.belt_ranks.all(),
                Division.c_team_belt_ranks)

    def test_competitor_too_young(self):
        competitor = Competitor.objects.create(name="competitor",
                sex=SexField.FEMALE_DB_VAL,
                skill_level=BeltRank.objects.get(belt_rank="WH"), age=19,
                organization=self.org1, weight=Decimal("115"))
        try:
            self.division_with_constraints.validate_competitor(competitor)
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError adding competitor too young")

    def test_competitor_too_young_no_constraints_division(self):
        competitor = Competitor.objects.create(name="competitor",
                sex=SexField.FEMALE_DB_VAL,
                skill_level=BeltRank.objects.get(belt_rank="WH"), age=19,
                organization=self.org1, weight=Decimal("115"))
        try:
            self.division_without_constraints.validate_competitor(competitor)
        except ValidationError:
            self.fail("Did not expect ValidationError adding competitor to"
                    + " division with no age limit")

    def test_competitor_too_old(self):
        competitor = Competitor.objects.create(name="competitor",
                sex=SexField.FEMALE_DB_VAL,
                skill_level=BeltRank.objects.get(belt_rank="WH"), age=31,
                organization=self.org1, weight=Decimal("115"))
        try:
            self.division_with_constraints.validate_competitor(competitor)
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError adding competitor too old")

    def test_competitor_too_light(self):
        competitor = Competitor.objects.create(name="competitor",
                sex=SexField.FEMALE_DB_VAL,
                skill_level=BeltRank.objects.get(belt_rank="WH"), age=25,
                organization=self.org1, weight=Decimal("105"))
        try:
            self.division_with_constraints.validate_competitor(competitor)
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError adding competitor too light")

    def test_competitor_too_heavy(self):
        competitor = Competitor.objects.create(name="competitor",
                sex=SexField.FEMALE_DB_VAL,
                skill_level=BeltRank.objects.get(belt_rank="WH"), age=25,
                organization=self.org1, weight=Decimal("125"))
        try:
            self.division_with_constraints.validate_competitor(competitor)
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError adding competitor too heavy")

    def test_competitor_invalid_sex(self):
        competitor = Competitor.objects.create(name="competitor",
                sex=SexField.MALE_DB_VAL,
                skill_level=BeltRank.objects.get(belt_rank="WH"), age=25,
                organization=self.org1, weight=Decimal("115"))
        try:
            self.division_with_constraints.validate_competitor(competitor)
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError adding male to female"
                    + " division")

    def test_competitor_invalid_belt_rank(self):
        competitor = Competitor.objects.create(name="competitor",
                sex=SexField.FEMALE_DB_VAL,
                skill_level=BeltRank.objects.get(belt_rank="BK"), age=25,
                organization=self.org1, weight=Decimal("115"))
        try:
            self.division_with_constraints.validate_competitor(competitor)
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError adding competitor with invalid"
                    + " BeltRank")

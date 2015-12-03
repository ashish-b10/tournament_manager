from django.test import TestCase
from tmdb.models import Organization, Competitor, SexField, BeltRank, Division
from tmdb.models import DivisionSkillField
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from decimal import Decimal
import itertools as it

class DivisionTestCase(TestCase):
    def setUp(self):
        BeltRank.create_tkd_belt_ranks()
        self.org1 = Organization.objects.create(name="org1")
        Division.create_ectc_divisions()

    def test_str(self):
        self.assertEqual("Women's A", str(Division.objects.get(
                sex=SexField.FEMALE_DB_VAL,
                skill_level=DivisionSkillField.A_TEAM_VAL)))
        self.assertEqual("Women's B", str(Division.objects.get(
                sex=SexField.FEMALE_DB_VAL,
                skill_level=DivisionSkillField.B_TEAM_VAL)))
        self.assertEqual("Women's C", str(Division.objects.get(
                sex=SexField.FEMALE_DB_VAL,
                skill_level=DivisionSkillField.C_TEAM_VAL)))
        self.assertEqual("Men's A", str(Division.objects.get(
                sex=SexField.MALE_DB_VAL,
                skill_level=DivisionSkillField.A_TEAM_VAL)))
        self.assertEqual("Men's B", str(Division.objects.get(
                sex=SexField.MALE_DB_VAL,
                skill_level=DivisionSkillField.B_TEAM_VAL)))
        self.assertEqual("Men's C", str(Division.objects.get(
                sex=SexField.MALE_DB_VAL,
                skill_level=DivisionSkillField.C_TEAM_VAL)))

    def test_duplicate_division_sex_skill(self):
        try:
            Division.objects.create(sex=SexField.MALE_DB_VAL,
                skill_level=DivisionSkillField.A_TEAM_VAL)
        except IntegrityError:
            pass
        else:
            self.fail("Creating divisions with same sex and skill_level"
                    + " should produce IntegrityError")

    def verify_division_belt_ranks(self, belt_ranks, expected_belt_rank_names):
        self.assertTrue(len(belt_ranks) == len(expected_belt_rank_names))
        belt_rank_names = {belt_rank.belt_rank for belt_rank in belt_ranks}
        self.assertTrue(belt_rank_names == set(expected_belt_rank_names))

    def test_ectc_division_belt_ranks(self):
        division = Division.objects.get(sex=SexField.FEMALE_DB_VAL,
                skill_level=DivisionSkillField.A_TEAM_VAL)
        self.verify_division_belt_ranks(division.belt_ranks.all(),
                Division.a_team_belt_ranks)
        division = Division.objects.get(sex=SexField.FEMALE_DB_VAL,
                skill_level=DivisionSkillField.B_TEAM_VAL)
        self.verify_division_belt_ranks(division.belt_ranks.all(),
                Division.b_team_belt_ranks)
        division = Division.objects.get(sex=SexField.FEMALE_DB_VAL,
                skill_level=DivisionSkillField.C_TEAM_VAL)
        self.verify_division_belt_ranks(division.belt_ranks.all(),
                Division.c_team_belt_ranks)
        division = Division.objects.get(sex=SexField.MALE_DB_VAL,
                skill_level=DivisionSkillField.A_TEAM_VAL)
        self.verify_division_belt_ranks(division.belt_ranks.all(),
                Division.a_team_belt_ranks)
        division = Division.objects.get(sex=SexField.MALE_DB_VAL,
                skill_level=DivisionSkillField.B_TEAM_VAL)
        self.verify_division_belt_ranks(division.belt_ranks.all(),
                Division.b_team_belt_ranks)
        division = Division.objects.get(sex=SexField.MALE_DB_VAL,
                skill_level=DivisionSkillField.C_TEAM_VAL)
        self.verify_division_belt_ranks(division.belt_ranks.all(),
                Division.c_team_belt_ranks)

    def test_competitor_invalid_sex(self):
        competitor = Competitor.objects.create(name="competitor",
                sex=SexField.MALE_DB_VAL,
                skill_level=BeltRank.objects.get(belt_rank="WH"), age=25,
                organization=self.org1, weight=Decimal("115"))
        female_division=Division.objects.get(sex=SexField.FEMALE_DB_VAL,
                skill_level=DivisionSkillField.C_TEAM_VAL)
        try:
            female_division.validate_competitor(competitor)
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
        female_division=Division.objects.get(sex=SexField.FEMALE_DB_VAL,
                skill_level=DivisionSkillField.C_TEAM_VAL)
        try:
            female_division.validate_competitor(competitor)
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError adding competitor with invalid"
                    + " BeltRank")

from django.test import TestCase
from tmdb.models import Organization, Competitor, Team, Division, Sex, BeltRank
from django.db.utils import IntegrityError
from decimal import Decimal
from django.core.exceptions import ValidationError
from unittest import skip

class TeamTestCase(TestCase):
    def setUp(self):
        Sex.create_sexes()
        BeltRank.create_tkd_belt_ranks()

        self.org1 = Organization(name="org1")
        self.org1.clean()
        self.org1.save()
        self.org2 = Organization(name="org2")
        self.org2.clean()
        self.org2.save()

        self.lightweight1 = Competitor(name="sample lightweight1",
                sex=Sex.FEMALE_SEX,
                skill_level=BeltRank.objects.get(belt_rank="WH"), age=20,
                organization=self.org1, weight=Decimal("117.0"))
        self.lightweight1.clean()
        self.lightweight1.save()
        self.middleweight1 = Competitor(name="sample middleweight1",
                sex=Sex.FEMALE_SEX,
                skill_level=BeltRank.objects.get(belt_rank="WH"), age=20,
                organization=self.org1, weight=Decimal("137.0"))
        self.middleweight1.clean()
        self.middleweight1.save()
        self.heavyweight1 = Competitor(name="sample heavyweight1",
                sex=Sex.FEMALE_SEX,
                skill_level=BeltRank.objects.get(belt_rank="WH"), age=20,
                organization=self.org1, weight=Decimal("157.0"))
        self.heavyweight1.clean()
        self.heavyweight1.save()

        self.division1 = Division(name="Women's D", sex=Sex.FEMALE_SEX)
        self.division1.clean()
        self.division1.save()
        self.division1.belt_ranks.add(BeltRank.objects.get(belt_rank="WH"))
        self.division1.clean()
        self.division1.save()

    def test_str(self):
        sample_team = Team(number=1, division=self.division1,
                organization=self.org1, lightweight=self.lightweight1)
        self.assertEqual("org1 Women's D1", str(sample_team))

    def test_invalid_organization(self):
        sample_team = Team(number=1, division=self.division1,
                organization=self.org2, lightweight=self.lightweight1)
        try:
            sample_team.clean()
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error adding Competitor to Team"
                    + " from different organizations")

    def test_set_lightweight_as_lightweight(self):
        sample_team = Team(number=1, division=self.division1,
                organization=self.org1, lightweight=self.lightweight1)
        sample_team.clean()
        sample_team.save()

    def test_set_middleweight_as_lightweight(self):
        sample_team = Team(number=1, division=self.division1,
                organization=self.org1, lightweight=self.middleweight1)
        try:
            sample_team.clean()
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error setting middleweight as"
                    + " lightweight")

    def test_set_heavyweight_as_lightweight(self):
        sample_team = Team(number=1, division=self.division1,
                organization=self.org1, lightweight=self.heavyweight1)
        try:
            sample_team.clean()
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error setting heavyweight as"
                    + " lightweight")

    def test_set_lightweight_as_middleweight(self):
        sample_team = Team(number=1, division=self.division1,
                organization=self.org1, middleweight=self.lightweight1)
        sample_team.clean()
        sample_team.save()

    def test_set_middleweight_as_middleweight(self):
        sample_team = Team(number=1, division=self.division1,
                organization=self.org1, middleweight=self.middleweight1)
        sample_team.clean()
        sample_team.save()

    def test_set_heavyweight_as_middleweight(self):
        sample_team = Team(number=1, division=self.division1,
                organization=self.org1, middleweight=self.heavyweight1)
        try:
            sample_team.clean()
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error setting heavyweight as"
                    + " middleweight")

    def test_set_lightweight_as_heavyweight(self):
        sample_team = Team(number=1, division=self.division1,
                organization=self.org1, heavyweight=self.lightweight1)
        try:
            sample_team.clean()
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error setting lightweight as"
                    + " heavyweight")

    def test_set_middleweight_as_heavyweight(self):
        sample_team = Team(number=1, division=self.division1,
                organization=self.org1, lightweight=self.lightweight1)
        sample_team.clean()
        sample_team.save()

    def test_set_heavyweight_as_heavyweight(self):
        sample_team = Team(number=1, division=self.division1,
                organization=self.org1, heavyweight=self.heavyweight1)
        sample_team.clean()
        sample_team.save()

    def test_set_lightweight_as_lightweight_and_middleweight_same_team(self):
        sample_team = Team(number=1, division=self.division1,
                organization=self.org1, lightweight=self.lightweight1,
                middleweight=self.lightweight1)
        try:
            sample_team.clean()
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error setting lightweight as both"
                    + " lightweight and middleweight positions on same team")

    def test_set_lightweight_as_lightweight_and_alternate1_same_team(self):
        sample_team = Team(number=1, division=self.division1,
                organization=self.org1, lightweight=self.lightweight1,
                alternate1=self.lightweight1)
        try:
            sample_team.clean()
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error setting lightweight as both"
                    + " lightweight and alternate1 positions on same team")

    def test_set_lightweight_as_alternate1_and_alternate2_same_team(self):
        sample_team = Team(number=1, division=self.division1,
                organization=self.org1, alternate1=self.lightweight1,
                alternate2=self.lightweight1)
        try:
            sample_team.clean()
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error setting lightweight as both"
                    + " lightweight and alternate1 positions on same team")

    def test_set_lightweight_as_lightweight_on_second_team(self):
        team1 = Team(number=1, division=self.division1, organization=self.org1,
                heavyweight=self.heavyweight1, lightweight=self.lightweight1)
        team1.clean()
        team1.save()
        team2 = Team(number=2, division=self.division1, organization=self.org1,
                middleweight=self.middleweight1, lightweight=self.lightweight1)
        try:
            team2.clean()
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error setting lightweight as"
                    + " lightweight when already lightweight on another team")

    def test_set_lightweight_as_middleweight_on_second_team(self):
        team1 = Team(number=1, division=self.division1, organization=self.org1,
                heavyweight=self.heavyweight1, lightweight=self.lightweight1)
        team1.clean()
        team1.save()
        team2 = Team(number=2, division=self.division1, organization=self.org1,
                heavyweight=self.middleweight1, middleweight=self.lightweight1)
        try:
            team2.clean()
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error setting lightweight as"
                    + " middleweight when already lightweight on another team")

    def test_set_lightweight_as_alternate1_on_second_team(self):
        team1 = Team(number=1, division=self.division1, organization=self.org1,
                heavyweight=self.heavyweight1, lightweight=self.lightweight1)
        team1.clean()
        team1.save()
        team2 = Team.objects.create(number=2, division=self.division1,
                organization=self.org1, middleweight=self.middleweight1,
                alternate1=self.lightweight1)
        try:
            team2.clean()
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error setting lightweight as"
                    + " alternate1 when already lightweight on another team")

    def test_set_alternate1_as_lightweight_on_second_team(self):
        team2 = Team(number=2, division=self.division1,
                organization=self.org1, middleweight=self.middleweight1,
                alternate1=self.lightweight1)
        team2.clean()
        team2.save()
        team1 = Team(number=1, division=self.division1,
                organization=self.org1, heavyweight=self.heavyweight1,
                lightweight=self.lightweight1)
        try:
            team1.clean()
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error setting lightweight as"
                    + " lightweight when already alternate1 on another team")

    def test_set_alternate1_as_alternate1_on_second_team(self):
        team1 = Team(number=1, division=self.division1, organization=self.org1,
                heavyweight=self.heavyweight1, alternate1=self.lightweight1)
        team1.clean()
        team1.save()
        team2 = Team(number=2, division=self.division1, organization=self.org1,
                middleweight=self.middleweight1, alternate1=self.lightweight1)
        team2.clean()
        team2.save()

    def test_set_alternate1_as_alternate2_on_second_team(self):
        team1 = Team(number=1, division=self.division1, organization=self.org1,
                heavyweight=self.heavyweight1, alternate1=self.lightweight1)
        team1.clean()
        team1.save()
        team2 = Team(number=2, division=self.division1, organization=self.org1,
                middleweight=self.middleweight1, alternate2=self.lightweight1)
        team2.clean()
        team2.save()

    def test_add_competitor_violating_division_constraints(self):
        sample_male_competitor = Competitor(name="sample male",
                sex=Sex.MALE_SEX,
                skill_level=BeltRank.objects.get(belt_rank="WH"), age=20,
                organization=self.org1, weight=Decimal("117.0"))
        sample_male_competitor.clean()
        sample_male_competitor.save()
        sample_team = Team(number=1, division=self.division1,
                organization=self.org1, lightweight=sample_male_competitor)
        try:
            sample_team.clean()
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error adding team member that does"
                    + " not satisfy division constraints")

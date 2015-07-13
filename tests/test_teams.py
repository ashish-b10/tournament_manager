from django.test import TestCase
from tmdb.models import Organization, Competitor, Team, Division
from django.db.utils import IntegrityError
from decimal import Decimal
from django.core.exceptions import ValidationError

class TeamTestCase(TestCase):
    def setUp(self):
        self.org1 = Organization.objects.create(name="org1")
        self.org2 = Organization.objects.create(name="org2")
        self.lightweight1 = Competitor.objects.create(
                name="sample lightweight1", sex="F", skill_level="WH", age=20,
                organization=self.org1, weight=Decimal("117.0"))
        self.middleweight1 = Competitor.objects.create(
                name="sample middleweight1", sex="F", skill_level="WH", age=20,
                organization=self.org1, weight=Decimal("137.0"))
        self.heavyweight1 = Competitor.objects.create(
                name="sample heavyweight1", sex="F", skill_level="WH", age=20,
                organization=self.org1, weight=Decimal("157.0"))
        self.division1 = Division.objects.create(skill_level="A", sex="F")

    def test_invalid_organization(self):
        try:
            sample_team = Team.objects.create(number=1,
                    division=self.division1, organization=self.org2,
                    lightweight=self.lightweight1)
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error adding Competitor to Team"
                    + " from different organizations")

    def test_set_lightweight_as_lightweight(self):
        sample_team = Team.objects.create(number=1,
                division=self.division1, organization=self.org1,
                lightweight=self.lightweight1)

    def test_set_middleweight_as_lightweight(self):
        try:
            sample_team = Team.objects.create(number=1,
                    division=self.division1, organization=self.org1,
                    lightweight=self.middleweight1)
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error setting middleweight as"
                    + " lightweight")

    def test_set_heavyweight_as_lightweight(self):
        try:
            sample_team = Team.objects.create(number=1,
                    division=self.division1, organization=self.org1,
                    lightweight=self.heavyweight1)
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error setting heavyweight as"
                    + " lightweight")

    def test_set_lightweight_as_middleweight(self):
        sample_team = Team.objects.create(number=1,
                division=self.division1, organization=self.org1,
                middleweight=self.lightweight1)

    def test_set_middleweight_as_middleweight(self):
        sample_team = Team.objects.create(number=1,
                division=self.division1, organization=self.org1,
                middleweight=self.middleweight1)

    def test_set_heavyweight_as_middleweight(self):
        try:
            sample_team = Team.objects.create(number=1,
                    division=self.division1, organization=self.org1,
                    middleweight=self.heavyweight1)
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error setting heavyweight as"
                    + " middleweight")

    def test_set_lightweight_as_heavyweight(self):
        try:
            sample_team = Team.objects.create(number=1,
                    division=self.division1, organization=self.org1,
                    heavyweight=self.lightweight1)
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error setting lightweight as"
                    + " heavyweight")

    def test_set_middleweight_as_heavyweight(self):
        sample_team = Team.objects.create(number=1,
                division=self.division1, organization=self.org1,
                lightweight=self.lightweight1)

    def test_set_heavyweight_as_heavyweight(self):
        sample_team = Team.objects.create(number=1,
                division=self.division1, organization=self.org1,
                heavyweight=self.heavyweight1)

    def test_set_lightweight_as_lightweight_and_middleweight_same_team(self):
        try:
            sample_team = Team.objects.create(number=1,
                    division=self.division1, organization=self.org1,
                    lightweight=self.lightweight1,
                    middleweight=self.lightweight1)
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error setting lightweight as both"
                    + " lightweight and middleweight positions on same team")

    def test_set_lightweight_as_lightweight_and_alternate1_same_team(self):
        try:
            sample_team = Team.objects.create(number=1,
                    division=self.division1, organization=self.org1,
                    lightweight=self.lightweight1,
                    alternate1=self.lightweight1)
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error setting lightweight as both"
                    + " lightweight and alternate1 positions on same team")

    def test_set_lightweight_as_alternate1_and_alternate2_same_team(self):
        try:
            sample_team = Team.objects.create(number=1,
                    division=self.division1, organization=self.org1,
                    alternate1=self.lightweight1,
                    alternate2=self.lightweight1)
        except ValidationError:
            pass
        else:
            self.fail("Expected validation error setting lightweight as both"
                    + " lightweight and alternate1 positions on same team")


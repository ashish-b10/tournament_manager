from django.test import TestCase
import tmdb.models as mdls
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

class TeamMatchTestCase(TestCase):
    def setUp(self):
        mdls.Sex.create_sexes()
        mdls.BeltRank.create_tkd_belt_ranks()
        self.division = mdls.Division.objects.create(name="test_division",
                sex=mdls.Sex.FEMALE_SEX)
        self.bracket = mdls.Bracket.objects.create(division=self.division)

    def test_root_team_match_valid(self):
        root_match = mdls.TeamMatch.objects.create(bracket=self.bracket,
                number=1, parent_side=0, root_match=True)
        self.assertTrue(root_match.has_root_match(),
                "has_root_match() returned False after creating root_match")

    def test_root_team_match_duplicate(self):
        root_match = mdls.TeamMatch.objects.create(bracket=self.bracket,
                number=1, parent_side=0, root_match=True)
        self.assertTrue(root_match.has_root_match(),
                "has_root_match() returned False after creating root_match")
        try:
            mdls.TeamMatch.objects.create(bracket=self.bracket, number=2,
                    parent_side=0, root_match=True)
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError creating second root_match")

    def test_duplicate_match_number(self):
        root_match = mdls.TeamMatch.objects.create(bracket=self.bracket,
                number=1, parent_side=0, root_match=True)
        self.assertTrue(root_match.has_root_match(),
                "has_root_match() returned False after creating root_match")
        try:
            mdls.TeamMatch.objects.create(bracket=self.bracket, number=1,
                    parent=root_match, parent_side=0, root_match=False)
        except IntegrityError:
            pass
        else:
            self.fail("Creating a second match with number=1 should raise"
                    + " IntegrityError")

    def test_root_team_match_invalid_parent_side(self):
        try:
            mdls.TeamMatch.objects.create(bracket=self.bracket, number=1,
                    parent_side=1, root_match=True)
        except ValidationError:
            pass
        else:
            self.fail("Creating root match with parent side != 0 should"
                    + " produce ValidationError")

    def test_nonroot_team_match_valid(self):
        root_match = mdls.TeamMatch.objects.create(bracket=self.bracket,
                number=1, parent_side=0, root_match=True)
        mdls.TeamMatch.objects.create(bracket=self.bracket, number=2,
                parent_side=0, parent=root_match, root_match=False)
        mdls.TeamMatch.objects.create(bracket=self.bracket, number=3,
                parent_side=1, parent=root_match, root_match=False)

    def test_nonroot_team_match_invalid_null_parent(self):
        root_match = mdls.TeamMatch.objects.create(bracket=self.bracket,
                number=1, parent_side=0, root_match=True)
        try:
            mdls.TeamMatch.objects.create(bracket=self.bracket, number=2,
                    parent_side=0, root_match=False)
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError creating non-root match with"
                    + " null parent")

    def test_nonroot_team_match_invalid_parent_side(self):
        root_match = mdls.TeamMatch.objects.create(bracket=self.bracket,
                number=1, parent_side=0, root_match=True)
        try:
            mdls.TeamMatch.objects.create(bracket=self.bracket, number=2,
                    parent_side=2, parent=root_match, root_match=False)
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError creating match with"
                    + " parent_side not in {0, 1}")

    def test_duplicate_nonroot_team_match(self):
        root_match = mdls.TeamMatch.objects.create(bracket=self.bracket,
                number=1, parent_side=0, root_match=True)
        mdls.TeamMatch.objects.create(bracket=self.bracket, number=2,
                parent_side=0, parent=root_match, root_match=False)
        try:
            mdls.TeamMatch.objects.create(bracket=self.bracket, number=3,
                    parent_side=0, parent=root_match, root_match=False)
        except IntegrityError:
            pass
        else:
            self.fail("Expected IntegrityError creating match with same"
                    + " (parent, parent_side)")

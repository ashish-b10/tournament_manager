from django.test import TestCase
import tmdb.models as mdls
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

class TeamMatchParticipantsTestCase(TestCase):
    def setUp(self):
        mdls.Sex.create_sexes()
        mdls.BeltRank.create_tkd_belt_ranks()
        self.division = mdls.Division.objects.create(name="test_division",
                sex=mdls.Sex.FEMALE_SEX)
        self.bracket = mdls.Bracket.objects.create(division=self.division)

        self.org1 = mdls.Organization.objects.create(name="org1")
        self.org2 = mdls.Organization.objects.create(name="org2")
        self.org1_team = mdls.Team.objects.create(number=1,
                division=self.division, organization = self.org1)
        self.org2_team = mdls.Team.objects.create(number=1,
                division=self.division, organization = self.org2)
        self.org2_team2 = mdls.Team.objects.create(number=2,
                division=self.division, organization = self.org2)

    def test_add_root_match_participant(self):
        root_match = mdls.TeamMatch.objects.create(bracket=self.bracket,
                number=1, parent_side=0, root_match=True)
        self.assertTrue(root_match.has_root_match(),
                "has_root_match() returned False after creating root_match")
        child_match = mdls.TeamMatch.objects.create(bracket=self.bracket,
                number=2, parent_side=0, parent=root_match, root_match=False)
        mdls.TeamMatchParticipant.objects.create(team_match=root_match,
                team=self.org1_team, slot_side=0)
        mdls.TeamMatchParticipant.objects.create(team_match=root_match,
                team=self.org2_team, slot_side=1)
        mdls.TeamMatchParticipant.objects.create(team_match=child_match,
                team=self.org2_team2, slot_side=0)
        match_teams = [p.team for p in
                mdls.TeamMatchParticipant.objects.filter(
                team_match=root_match)]
        self.assertEqual(len(match_teams), 2, "There are two teams in"
                + " root_match")
        self.assertEqual(set(match_teams), {self.org1_team, self.org2_team},
                "org1_team and org2_team are the teams in root_match")

    def test_add_participant_duplicate_slot_side(self):
        root_match = mdls.TeamMatch.objects.create(bracket=self.bracket,
                number=1, parent_side=0, root_match=True)
        self.assertTrue(root_match.has_root_match(),
                "has_root_match() returned False after creating root_match")
        mdls.TeamMatchParticipant.objects.create(team_match=root_match,
                team=self.org1_team, slot_side=0)
        try:
            mdls.TeamMatchParticipant.objects.create(team_match=root_match,
                    team=self.org2_team, slot_side=0)
        except IntegrityError:
            pass
        else:
            self.fail("Expected IntegrityError adding multiple entries for"
                    + "  same match and slot_side")

    def test_add_participant_duplicate_team(self):
        root_match = mdls.TeamMatch.objects.create(bracket=self.bracket,
                number=1, parent_side=0, root_match=True)
        self.assertTrue(root_match.has_root_match(),
                "has_root_match() returned False after creating root_match")
        mdls.TeamMatchParticipant.objects.create(team_match=root_match,
                team=self.org1_team, slot_side=0)
        try:
            mdls.TeamMatchParticipant.objects.create(team_match=root_match,
                    team=self.org1_team, slot_side=1)
        except IntegrityError:
            pass
        else:
            self.fail("Expected IntegrityError adding multiple entries for"
                    + " same TeamMatch and Team")

    def test_add_participant_invalid_slot_side(self):
        root_match = mdls.TeamMatch.objects.create(bracket=self.bracket,
                number=1, parent_side=0, root_match=True)
        self.assertTrue(root_match.has_root_match(),
                "has_root_match() returned False after creating root_match")
        try:
            mdls.TeamMatchParticipant.objects.create(team_match=root_match,
                    team=self.org1_team, slot_side=2)
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError creating TeamMatchParticipant"
                    + " with slot_side not in {0, 1}")

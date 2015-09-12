from django.test import TestCase
import tmdb.models as mdls
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

class TeamMatchParticipantsTestCase(TestCase):
    def setUp(self):
        mdls.Sex.create_sexes()
        mdls.BeltRank.create_tkd_belt_ranks()
        self.division = mdls.Division(name="test_division",
                sex=mdls.Sex.FEMALE_SEX)
        self.division.clean()
        self.division.save()

        self.org1 = mdls.Organization(name="org1")
        self.org1.clean()
        self.org1.save()
        self.org2 = mdls.Organization(name="org2")
        self.org2.clean()
        self.org2.save()

        self.org1_team = mdls.Team(number=1, division=self.division,
                organization = self.org1)
        self.org1_team.clean()
        self.org1_team.save()
        self.org2_team = mdls.Team(number=1, division=self.division,
                organization = self.org2)
        self.org2_team.clean()
        self.org2_team.save()
        self.org2_team2 = mdls.Team(number=2, division=self.division,
                organization = self.org2)
        self.org2_team2.clean()
        self.org2_team2.save()

    def test_add_root_match_participant(self):
        root_match = mdls.TeamMatch(division=self.division, number=1,
                parent_side=0, root_match=True)
        root_match.clean()
        root_match.save()
        self.assertTrue(root_match.has_root_match(),
                "has_root_match() returned False after creating root_match")

        child_match = mdls.TeamMatch(division=self.division, number=2,
                parent_side=0, parent=root_match, root_match=False)
        child_match.clean()
        child_match.save()

        participant1 = mdls.TeamMatchParticipant(team_match=root_match,
                team=self.org1_team, slot_side=0)
        participant1.clean()
        participant1.save()
        participant2 = mdls.TeamMatchParticipant(team_match=root_match,
                team=self.org2_team, slot_side=1)
        participant2.clean()
        participant2.save()
        participant3 = mdls.TeamMatchParticipant(team_match=child_match,
                team=self.org2_team2, slot_side=0)
        participant3.clean()
        participant3.save()
        match_teams = [p.team for p in
                mdls.TeamMatchParticipant.objects.filter(
                team_match=root_match)]

        self.assertEqual(len(match_teams), 2, "There are two teams in"
                + " root_match")
        self.assertEqual(set(match_teams), {self.org1_team, self.org2_team},
                "org1_team and org2_team are the teams in root_match")

    def test_add_participant_duplicate_slot_side(self):
        root_match = mdls.TeamMatch(division=self.division, number=1,
                parent_side=0, root_match=True)
        root_match.clean()
        root_match.save()
        self.assertTrue(root_match.has_root_match(),
                "has_root_match() returned False after creating root_match")

        participant1 = mdls.TeamMatchParticipant(team_match=root_match,
                team=self.org1_team, slot_side=0)
        participant1.clean()
        participant1.save()
        participant2 = mdls.TeamMatchParticipant(team_match=root_match,
                team=self.org2_team, slot_side=0)
        participant2.clean()
        try:
            participant2.save()
        except IntegrityError:
            pass
        else:
            self.fail("Expected IntegrityError adding multiple entries for"
                    + "  same match and slot_side")

    def test_add_participant_duplicate_team(self):
        root_match = mdls.TeamMatch(division=self.division, number=1,
                parent_side=0, root_match=True)
        root_match.clean()
        root_match.save()
        self.assertTrue(root_match.has_root_match(),
                "has_root_match() returned False after creating root_match")

        participant1 = mdls.TeamMatchParticipant(team_match=root_match,
                team=self.org1_team, slot_side=0)
        participant1.clean()
        participant1.save()
        participant2 = mdls.TeamMatchParticipant(team_match=root_match,
                team=self.org1_team, slot_side=1)
        participant2.clean()
        try:
            participant2.save()
        except IntegrityError:
            pass
        else:
            self.fail("Expected IntegrityError adding multiple entries for"
                    + " same TeamMatch and Team")

    def test_add_participant_invalid_slot_side(self):
        root_match = mdls.TeamMatch(division=self.division, number=1,
                parent_side=0, root_match=True)
        root_match.clean()
        root_match.save()
        self.assertTrue(root_match.has_root_match(),
                "has_root_match() returned False after creating root_match")
        participant1 = mdls.TeamMatchParticipant(team_match=root_match,
                team=self.org1_team, slot_side=2)
        try:
            participant1.clean()
        except ValidationError:
            pass
        else:
            self.fail("Expected ValidationError creating TeamMatchParticipant"
                    + " with slot_side not in {0, 1}")

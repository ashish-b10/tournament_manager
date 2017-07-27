"""
Team Match Model

Last Updated: 07-25-2017
"""
# Django imports
from django.db import models
from tmdb.util import BracketGenerator
# Model imports
from . import *

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
    division = models.ForeignKey('TournamentDivision')
    number = models.PositiveIntegerField()
    round_num = models.SmallIntegerField()
    round_slot = models.IntegerField()
    blue_team = models.ForeignKey('TeamRegistration', related_name="blue_team",
            blank=True, null=True)
    red_team = models.ForeignKey('TeamRegistration', related_name="red_team",
            blank=True, null=True)
    ring_number = models.PositiveIntegerField(blank=True, null=True)
    ring_assignment_time = models.DateTimeField(blank=True, null=True)
    winning_team = models.ForeignKey('TeamRegistration', blank=True, null=True,
            related_name="winning_team")
    in_holding = models.BooleanField(default=False)

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

    @staticmethod
    def create_matches_from_slots(tournament_division):
        TeamMatch.objects.filter(division=tournament_division).delete()
        seeded_teams = TeamRegistration.objects.filter(
                tournament_division=tournament_division, seed__isnull=False)
        seeds = {team.seed:team for team in seeded_teams}
        start_val = tournament_division.division.match_number_start_val()
        bracket = BracketGenerator(seeds, match_number_start_val=start_val)
        for bracket_match in bracket:
            match = TeamMatch(division=tournament_division,
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
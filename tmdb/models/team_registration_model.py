"""
Team Registration Model

Last Updated: 07-25-2017
"""

# Django imports
from django.db import models

from tmdb.util import BracketGenerator, SlotAssigner

#TODO team.division must equal tournament_division.division
class TeamRegistration(models.Model):
    tournament_division = models.ForeignKey('TournamentDivision')
    team = models.ForeignKey('Team')
    seed = models.PositiveSmallIntegerField(null=True, blank=True)
    points = models.PositiveIntegerField(null=True, blank=True)
    lightweight = models.ForeignKey('Competitor', null=True, blank=True,
            related_name="lightweight", on_delete=models.deletion.SET_NULL)
    middleweight = models.ForeignKey('Competitor', null=True, blank=True,
            related_name="middleweight", on_delete=models.deletion.SET_NULL)
    heavyweight = models.ForeignKey('Competitor', null=True, blank=True,
            related_name="heavyweight", on_delete=models.deletion.SET_NULL)
    alternate1 = models.ForeignKey('Competitor', null=True, blank=True,
            related_name="alternate1", on_delete=models.deletion.SET_NULL)
    alternate2 = models.ForeignKey('Competitor', null=True, blank=True,
            related_name="alternate2", on_delete=models.deletion.SET_NULL)

    class Meta:
        unique_together = (('tournament_division', 'team'),
                ('tournament_division', 'seed'),)

    def __get_competitors_str(self):
        lightweight = "L" if self.lightweight else ""
        middleweight = "M" if self.middleweight else ""
        heavyweight = "H" if self.heavyweight else ""
        if not lightweight and not middleweight and not heavyweight:
            return ""
        return "(" + lightweight + middleweight + heavyweight + ")"

    def get_competitors_ids(self):
        competitors = []
        if self.lightweight:
            competitors.append(self.lightweight.id)
        if self.middleweight:
            competitors.append(self.middleweight.id)
        if self.heavyweight:
            competitors.append(self.heavyweight.id)
        return competitors

    def __str__(self):
        competitors_str = self.__get_competitors_str()
        if competitors_str:
            competitors_str = " " + competitors_str
        return "%s%s" %(str(self.team), competitors_str)

    def __repr__(self):
        return "%s (%s)" %(str(self.team),
                str(self.tournament_division.tournament),)

    def bracket_str(self):
        team_str = "%s %s%d %s" %(self.team.school,
                self.team.division.skill_level,
                self.team.number,
                self.__get_competitors_str())
        if self.seed:
            team_str = "[%d] %s" %(self.seed, team_str)
        return team_str

    def num_competitors(self):
        return sum(map(lambda x: x is not None,
                [self.lightweight, self.middleweight, self.heavyweight]))

    @classmethod
    def get_teams_with_assigned_slots(cls, tournament_division):
        """
        Assigns all teams in tournament_division to a slot in the
        bracket. Returns a dict of {team:seed}.
        """
        teams = cls.objects.filter(tournament_division=tournament_division).order_by('team__number').order_by('team__school')
        get_num_competitors = lambda team: team.num_competitors()
        slot_assigner = SlotAssigner(list(teams), 4,
                get_school_name = lambda team: team.team.school.name,
                get_points = lambda team: team.points if team.points else 0)
        for team in teams:
            team.seed = slot_assigner.slots_by_team.get(team)
        return teams

    @classmethod
    def get_teams_without_assigned_slot(cls, tournament_division):
        """
        Returns a list of teams that do not have a slot in the bracket.

        Currently, the condition for this is TeamRegistration.seed is
        empty.
        """
        return cls.objects.filter(
                tournament_division=tournament_division, seed__isnull=True) \
                .order_by('team__school__name', 'team__number')

    @staticmethod
    def order_queryset(query_set):
        return query_set.order_by('team__school__name',
                'tournament_division__division', 'team__number')
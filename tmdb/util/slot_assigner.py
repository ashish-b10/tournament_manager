from collections import defaultdict
import random
import itertools as it

import logging
logger = logging.getLogger(__name__)

__all__ = ["SlotAssignerException", "SlotAssigner"]

def _group_by(group_function, items):
    grouped_items = defaultdict(list)
    for item in items:
        grouped_items[group_function(item)].append(item)
    return grouped_items

def _order_groups_by_size(groups):
    ordered_groups = defaultdict(list)
    for group_name,group_values in groups.items():
        #ordered_groups[len(group_values)].append((group_name, group_values))
        ordered_groups[len(group_values)].append(group_values)

    for key in sorted(ordered_groups.keys(), reverse=True):
        for vals in ordered_groups[key]:
            #yield key, vals
            yield vals

def _next_power_of_2(num):
    """ Returns the smallest power of 2 >= num. """
    if num <= 0:
        return 0
    next_power = 1
    while next_power < num:
        next_power <<= 1
    return next_power

class SlotAssignerException(Exception): pass

class SlotAssigner:
    def __init__(self, teams, num_seeds, get_school_name=None,
            get_points=None):
        self.teams = teams
        # FIXME do not assign one-person teams for now
        self._drop_one_person_teams()
        self.num_teams = len(self.teams)
        self.num_seeds = num_seeds
        self.get_school_name = get_school_name
        if self.get_school_name is None:
            self.get_school_name = lambda team: team.school_name
        self.get_points = get_points
        if self.get_points is None:
            self.get_points = lambda team: team.points
        self.teams_grouped_by_school = _group_by(
                self.get_school_name, self.teams)
        self.slots = {}
        self.slots_by_team = {}
        self._compute_bracket()

    def _drop_one_person_teams(self):
        all_teams = self.teams
        filtered_teams = list(filter(
                lambda team: team.num_competitors() >= 2, self.teams))
        ignored_teams = map(str, set(all_teams) - set(filtered_teams))
        logger.warn("Ignoring one-person teams: " + ", ".join(ignored_teams))
        self.teams = filtered_teams

    def _compute_bracket(self):
        self._assign_seeds(self.num_seeds)
        self._assign_remaining_multi_person_teams()

    def _is_slotted(self, school_team):
        """ Returns whether school_team has already been assigned a
        slot."""
        return school_team in self.slots_by_team

    def _assign_remaining_multi_person_teams(self):
        sorted_groups = _order_groups_by_size(self.teams_grouped_by_school)
        for school_teams in sorted_groups:
            for school_team in school_teams:
                if self._is_slotted(school_team):
                    continue
                self.assign_slot(school_team)

    def assign_slot(self, team):
        for num_partitions in [1,2,4,8,16,32,64,128]:
            slot_groups = self._partition_slots(num_partitions)
            slot_groups = self._prune_slot_groups_with_team_from_same_school(
                    slot_groups, self.get_school_name(team))
            slot_groups = self._prune_filled_slot_groups(slot_groups)
            if slot_groups:
                break

        # select the largest slot_group and assign the team to one of the slots
        # we must use the largest one because otherwise, all but one group may
        # fill and two schools from a later team might get grouped together
        # earlier than they should
        random.shuffle(slot_groups)
        max_slot_group_size = 0
        for slot_group in slot_groups:
            slot_group_size = len(slot_group)
            if slot_group_size > max_slot_group_size:
                max_slot_group_size = slot_group_size
                slot = random.sample(slot_group, 1)[0]
        self.set_slot(team, slot)

    def _partition_slots(self, num_partitions):
        """ Groups the slots of the bracket by which partition (half,
            quarter, etc.) they are in.

        >>> partition_slots(15, 1)
        [{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}]
        >>> partition_slots(15, 2)
        [{1, 4, 5, 8, 9, 12, 13}, {2, 3, 6, 7, 10, 11, 14, 15}]
        >>> partition_slots(15, 4)
        [{8, 1, 9}, {15, 2, 10, 7}, {3, 11, 6, 14}, {4, 5, 12, 13}]
        """
        if num_partitions < 1:
            raise ArgumentError("Must have at least one partition")

        brackets = [set() for i in range(num_partitions)]
        forward_groups = range(num_partitions)
        backward_groups = reversed(forward_groups)
        iteration_order = it.cycle(it.chain(forward_groups, backward_groups))
        for slot, group_num in enumerate(it.islice(
                iteration_order, self.num_teams)):
            brackets[group_num].add(slot + 1)
        return brackets

    def _prune_slot_groups_with_team_from_same_school(self, slot_groups,
            school_name):
        """Return all slot groups which do not already have a team from
        this school"""
        pruned_slot_groups = []
        for slots in slot_groups:
            team_found = False
            for slot in slots:
                slotted_team = self.slots.get(slot)
                if slotted_team is None:
                    continue
                if self.get_school_name(slotted_team) == school_name:
                    team_found = True
                    break
            if not team_found:
                pruned_slot_groups.append(slots)

        return pruned_slot_groups

    def _prune_filled_slot_groups(self, slot_groups):
        pruned_slot_groups = []
        for slots in slot_groups:
            pruned_slot_group = set()
            for slot in slots:
                if slot not in self.slots:
                    pruned_slot_group.add(slot)
            if pruned_slot_group:
                pruned_slot_groups.append(pruned_slot_group)
        return pruned_slot_groups

    def _assign_seeds(self, min_num_seeds):
        """ Calculates all the teams that deserve a seed and inserts
            them in the appropriate location of the bracket. This method
            should also break ties and assign seeds for all those ties
            (if desired)."""
        grouped_teams = _group_by(self.get_points, self.teams)

        seeded_teams = []
        point_vals = sorted(grouped_teams.keys())
        while len(seeded_teams) < min_num_seeds and point_vals:
            # get the highest point count that has not yet been assigned
            point_val = point_vals.pop()
            if point_val == 0:
                break

            # get all teams with this number of points
            point_group = grouped_teams[point_val]
            logger.info("Seeding %d teams with %d points: %s" %(
                    len(point_group), point_val, ", ".join(
                            map(str, point_group))))
            # remove one-person teams because they cannot have a seed
            point_group = list(filter(
                    lambda team: team.num_competitors() >= 2,
                    point_group))

            # break ties by shuffling all teams in the same group of points
            random.shuffle(point_group)
            seeded_teams.extend(point_group)

        for slot_num, seeded_team in enumerate(seeded_teams):
            self.set_slot(seeded_team, slot_num + 1)

    def set_slot(self, team, slot_num):
        logger.info("Assigning %s to %d" %(team, slot_num))
        self.slots[slot_num] = team
        self.slots_by_team[team] = slot_num

    def pprint(self):
        strs = []
        for i in range(self.num_teams):
            slot = i + 1
            strs.append("slot %3d: %s" %(slot, self.slots.get(slot)))
        return "\n".join(strs)


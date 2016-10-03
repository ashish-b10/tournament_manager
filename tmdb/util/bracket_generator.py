#!/usr/bin/env python3

__all__ = ["BracketGenerator"]

class Team():
    def __init__(self, team_name = None):
        if isinstance(team_name, str):
            self.team_name = lambda: team_name

    def __str__(self):
        return self.team_name()

class BracketNode():

    UPPER_SIDE = 0
    LOWER_SIDE = 1

    def __init__(self, bracket, round_num, round_slot):
        self.bracket = bracket
        self.round_num = round_num
        self.round_slot = round_slot
        self.blue_team = self.red_team = None

    def _set_teams(self, seeds):
        upper_seeds = {}
        lower_seeds = {}
        for seed_num, team in seeds.items():
            match_side = self._get_side_of_match(seed_num - 1, self.round_num)
            if match_side == BracketNode.UPPER_SIDE:
                upper_seeds[seed_num] = team
                continue
            if match_side == BracketNode.LOWER_SIDE:
                lower_seeds[seed_num] = team
                continue
            raise Exception("Unexpected result from"
                    " BracketNode._get_side_of_match: %d" %(match_side))

        if len(upper_seeds) > 1:
            upper_predecessor = BracketNode(
                    self.bracket, self.round_num + 1, self.round_slot * 2)
            self.bracket._add_bracket_node(upper_predecessor)
            upper_predecessor._set_teams(upper_seeds)
        elif len(upper_seeds) == 1:
            self.blue_team = next(iter(upper_seeds.values()))

        if len(lower_seeds) > 1:
            lower_predecessor = BracketNode(
                    self.bracket, self.round_num + 1, self.round_slot * 2 + 1)
            self.bracket._add_bracket_node(lower_predecessor)
            lower_predecessor._set_teams(lower_seeds)
        elif len(lower_seeds) == 1:
            self.red_team = next(iter(lower_seeds.values()))

    def _get_previous_round_match(self, match_side):
        upper_side, lower_side = self._get_previous_round_matches()
        if match_side == BracketNode.UPPER_SIDE:
            return upper_side
        if match_side == BracketNode.LOWER_SIDE:
            return lower_side
        raise AttributeError("Invalid value for match_side: %d" %(match_side))

    def _get_previous_round_matches(self):
        return (self.bracket._get_bracket_node(
                self.round_num + 1, self.round_slot * 2),
                self.bracket._get_bracket_node(
                self.round_num + 1, self.round_slot * 2 + 1),)

    _cached_match_side_values = {(0, 0,): False, (1, 0,): True, (2, 0,): True,
                (3, 0,): False}
    @staticmethod
    def _get_side_of_match(seed, round_num):

        pivot = 2 ** (round_num + 2)
        seed %= pivot
        cached_value = BracketNode._cached_match_side_values.get(
                (seed, round_num,))
        if cached_value is not None: return cached_value

        result = BracketNode._get_side_of_match(seed, round_num - 1)
        if seed >= pivot // 4 and seed < pivot * 3 // 4:
            result = not result
        BracketNode._cached_match_side_values[(seed, round_num,)] = result
        return result

    def is_bye(self):
        upper_pred, lower_pred = self._get_previous_round_matches()
        if upper_pred:
            upper_match_is_bye = upper_pred.is_bye()
        else:
            upper_match_is_bye = not bool(self.blue_team)

        if upper_match_is_bye:
            return True

        if lower_pred:
            lower_match_is_bye = lower_pred.is_bye()
        else:
            lower_match_is_bye = not bool(self.red_team)

        if lower_match_is_bye:
            return True

        return False

    def _render_pprint(self):
        indent = " " * 8
        if self.blue_team:
            blue_team_name = self.blue_team.team_name()
        else:
            upper_pred = self._get_previous_round_match(BracketNode.UPPER_SIDE)
            if not upper_pred or upper_pred.is_bye():
                blue_team_name = "bye"
            else:
                blue_team_name = "|"

        if self.red_team:
            red_team_name = self.red_team.team_name()
        else:
            lower_pred = self._get_previous_round_match(BracketNode.LOWER_SIDE)
            if not lower_pred or lower_pred.is_bye():
                red_team_name = "bye"
            else:
                red_team_name = "|"

        print((indent * (self.round_num + 1)) + blue_team_name)
        if self.number:
            print((indent * self.round_num) + "m#" + str(self.number))
        print((indent * (self.round_num + 1)) + red_team_name)

    def pprint(self):
        upper_pred, lower_pred = self._get_previous_round_matches()
        if upper_pred:
            upper_pred.pprint()

        self._render_pprint()

        if lower_pred:
            lower_pred.pprint()

class BracketGenerator():

    def __init__(self, seeds, match_number_start_val):
        self.matches = {}
        self.seeds = seeds
        self._add_bracket_node(BracketNode(self, 0, 0))
        self._set_seeds(self.seeds)
        self._assign_match_numbers(match_number_start_val)

    def _set_seeds(self, seeds):
        self._get_bracket_node(0, 0)._set_teams(seeds)

    def _get_bracket_node(self, round_num, round_slot):
        return self.matches.get((round_num, round_slot,))

    def _add_bracket_node(self, bracket_node):
        round_num = bracket_node.round_num
        round_slot = bracket_node.round_slot
        self.matches[(round_num, round_slot,)] = bracket_node

    def _assign_match_numbers(self, match_number_start_val):
        match_keys = self._sorted_match_keys()
        for match_key in match_keys:
            match = self.matches[match_key]
            if match.is_bye():
                match.number = None
                continue
            match.number = match_number_start_val
            match_number_start_val+= 1

    def _sorted_match_keys(self):
        match_keys = list(self.matches.keys())
        match_keys.sort(reverse=True, key = lambda x: (x[0], -x[1]))
        return match_keys

    def __iter__(self):
        return BracketIterator(self)

    @staticmethod
    def create_from_teams_file(filename):
        seeds = {}
        with open(filename, 'r') as fh:
            for line in fh:
                line = line.rstrip()
                if not line:
                    continue
                team_name, seed_num = line.split(',')
                seed_num = int(seed_num)
                seeds[seed_num] = Team(team_name)
        return BracketGenerator(seeds, match_number_start_val=101)

    def pprint(self):
        return self._get_bracket_node(0,0).pprint()

class BracketIterator():

    def __init__(self, bracket_generator):
        self.bracket_generator = bracket_generator
        self.match_keys_iterator = iter(
                self.bracket_generator._sorted_match_keys())

    def __next__(self):
        match_key = next(self.match_keys_iterator)
        return self.bracket_generator._get_bracket_node(*match_key)

if __name__ == "__main__":
    bracket = BracketGenerator.create_from_teams_file('seeds.txt')
    for match in bracket:
        print("%d: %s vs. %s" %(match.number, match.blue_team, match.red_team,))
    bracket.pprint()

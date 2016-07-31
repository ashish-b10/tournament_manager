from collections import deque

__all__ = ["BracketGenerator"]

class Team():
    def __init__(self, team_num, team_name = None):
        self.team_num = team_num
        if team_name is not None:
            self.team_name = team_name

    def team_name(self):
        try:
            return self.team_name
        except AttributeError:
            return str(self.team_num)

class BracketNode():
    def __init__(self, bracket):
        self.bracket = bracket

    @staticmethod
    def _split_bracket(seeds, lower_bracket=False):
        lower_seeds = []
        upper_seeds = []
        for seed_num, seed in enumerate(seeds):
            if seed is None: continue
            if (seed_num + 1) & 2:
                lower_seeds.append(seed)
            else:
                upper_seeds.append(seed)
        if lower_bracket:
            upper_seeds, lower_seeds = lower_seeds, upper_seeds
        return upper_seeds, lower_seeds

    @staticmethod
    def _create_from_seeds(bracket, seeds, lower_bracket=False):
        b = BracketNode(bracket)

        if not seeds:
            return b

        # if len(seeds) == 1:
        try:
            seeds[1]
        except IndexError:
            b.seed = seeds[0]
            return b

        upper_seeds, lower_seeds = BracketNode._split_bracket(seeds,
                lower_bracket)
        b.upper_slot = BracketNode._create_from_seeds(bracket, upper_seeds,
                False)
        b.lower_slot = BracketNode._create_from_seeds(bracket, lower_seeds,
                True)
        return b

    def bfs(self, seeds=True, matches=True):
        bracket_queue = deque([self])
        while True:
            try:
                bracket_node = bracket_queue.popleft()
            except IndexError:
                break
            if bracket_node.is_match():
                bracket_queue.append(bracket_node.lower_slot)
                bracket_queue.append(bracket_node.upper_slot)
                if matches:
                    yield bracket_node
            elif seeds:
                yield bracket_node

    def is_match(self):
        return not hasattr(self, 'seed')

    def seed_name(self):
        if hasattr(self, 'team'):
            return self.team.team_name()
        return "bye"

    def __str__(self):
        if self.is_match():
            return str(self.number)
        else:
            return '[%d] %s' %(self.seed, self.seed_name())

    def pprint(self, num_indent=0, indent=' ' * 8):
        if not self.is_match():
            return (num_indent * indent) + str(self)

        upper_slot_str = self.upper_slot.pprint(num_indent + 1)
        lower_slot_str = self.lower_slot.pprint(num_indent + 1)

        match_str = (num_indent * indent) + "m#" + str(self.number)
        return "\n".join([upper_slot_str, match_str, lower_slot_str])

class BracketGenerator():

    UPPER_SIDE = 0
    LOWER_SIDE = 1

    def __init__(self, seeds, match_number_start_val=100):
        try:
            num_seeds = max(seeds.keys())
        except ValueError:
            num_seeds = 1
        self.root = BracketNode._create_from_seeds(self,
                list(range(1, 1 + num_seeds)))
        self.matches = self._create_matches_index(match_number_start_val)
        self.seeds = self._seeds_index()
        self._evaluate_parents()
        for seed_num, team in seeds.items():
            self.seeds[seed_num].team = team

    def _seeds_index(self):
        seeds = {}
        for match_seed in self.root.bfs(matches=False):
            seeds[match_seed.seed] = match_seed
        return seeds

    def _create_matches_index(self, match_number_start_val):
        match_number = match_number_start_val
        for match in list(self.root.bfs(seeds=False))[::-1]:
            match.number = match_number
            match_number += 1

    def _evaluate_parents(self):
        self.root.parent = None
        self.root.parent_side = BracketGenerator.UPPER_SIDE
        self.root.is_root = True
        self.root.round_num = 0
        self.root.round_slot = self.root.parent_side
        for match in self.root.bfs(seeds=False):
            match.upper_slot.parent = match
            match.upper_slot.parent_side = BracketGenerator.UPPER_SIDE
            match.upper_slot.is_root = False
            match.upper_slot.round_num = match.round_num + 1
            match.upper_slot.round_slot = 2*match.round_slot + match.upper_slot.parent_side
            if not match.upper_slot.is_match():
                match.blue_team = match.upper_slot
            match.lower_slot.parent = match
            match.lower_slot.parent_side = BracketGenerator.LOWER_SIDE
            match.lower_slot.is_root = False
            match.lower_slot.round_num = match.round_num + 1
            match.lower_slot.round_slot = 2*match.round_slot + match.lower_slot.parent_side
            if not match.lower_slot.is_match():
                match.red_team = match.lower_slot

    def bfs(self, *args, **kwargs):
        return self.root.bfs(*args, **kwargs)

    def pprint(self):
        return self.root.pprint()

    @staticmethod
    def create_from_teams_file(filename):
        seeds = {}
        with open(filename, 'r') as fh:
            for line in fh:
                line = line.rstrip()
                if not line:
                    continue
                team, seed_num = line.split(',')
                seed_num = int(seed_num)
                seeds[seed_num] = team
        return BracketGenerator(seeds)

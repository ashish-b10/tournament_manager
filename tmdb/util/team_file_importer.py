import csv
import re
from io import StringIO
from collections import defaultdict

from tmdb import models

NUM_TEAMS_RE = re.compile('(?P<num_teams>\d+) Teams')

__all__ = ['parse_team_file']

DIVISION_NAMES = [
    "Men's A",
    "Women's A",
    "Men's B",
    "Women's B",
    "Men's C",
    "Women's C",
]

def _generate_division_re(division_name):
    return re.compile(f' {division_name}(?P<team_num>\d+) - \('
            + '(?P<has_lightweight>L?)'
            + '(?P<has_middleweight>M?)'
            + '(?P<has_heavyweight>H?)'
            + '\)$')

def parse_team_file(team_file):
    team_file_data = team_file.read().decode('utf-8')
    teams_fh = StringIO(team_file_data)
    teams_csv = csv.DictReader(teams_fh)
    # ignore first two rows of the file (they are empty)
    num_teams = _parse_num_teams(next(teams_csv))
    next(teams_csv)

    teams = defaultdict(list)

    division_re_patterns = {}
    for division_name in DIVISION_NAMES:
        division_re_patterns[division_name] = _generate_division_re(
                division_name)

    for team_row in teams_csv:
        for division_name in DIVISION_NAMES:
            if not team_row[division_name]:
                continue
            sparring_division = _get_sparring_division(division_name)
            team_cell = team_row[division_name]
            match = division_re_patterns[division_name].search(team_cell)
            school_name = team_cell[:match.span()[0]]
            team_data = {
                    'sparring_division': sparring_division,
                    'school_name': school_name,
                    'team_num': int(match.group('team_num')),
                    'has_lightweight': bool(match.group('has_lightweight')),
                    'has_middleweight': bool(match.group('has_middleweight')),
                    'has_heavyweight': bool(match.group('has_heavyweight')),
            }
            teams[division_name].append(team_data)
    for division_name in DIVISION_NAMES:
        assert len(teams[division_name]) == num_teams[division_name]
    return teams

def _parse_num_teams(num_teams_row):
    num_teams = {}
    for division_name in DIVISION_NAMES:
        match = re.match(NUM_TEAMS_RE, num_teams_row[division_name])
        num_teams[division_name] = int(match.group('num_teams'))
    return num_teams

def _get_sparring_division(division_name):
    sex = division_name[:-1].strip()
    skill_level = division_name[-1:]
    if sex == "Men's":
        sex = models.SexField.MALE
    elif sex == "Women's":
        sex = models.SexField.FEMALE
    else:
        raise ValueError(f"Unrecognized division_name: [{division_name}]")
    return models.SparringDivision.objects.get(sex=sex, skill_level=skill_level)

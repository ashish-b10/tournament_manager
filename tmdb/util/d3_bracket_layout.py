__all__ = ['d3_bracket_layout']

def d3_bracket_layout(tournament_division, matches_by_round):
    if not matches_by_round:
        return {}
    if (0,0,) not in matches_by_round:
        return None
    root_match = matches_by_round[(0,0,)]
    return __get_d3_bracket_layout(root_match, matches_by_round)

def __get_upper_competitor(match, matches_by_round):
    return matches_by_round.get((
            match.round_num + 1, match.round_slot * 2,))

def __get_lower_competitor(match, matches_by_round):
    return matches_by_round.get((
            match.round_num + 1, match.round_slot * 2 + 1,))

def __get_d3_round_name(match):
    if match.winning_team:
        return match.winning_team.team.short_str()
    return str(match)

def __get_d3_bracket_layout(match, matches_by_round, side=None):
    layout = {}
    layout['name'] = __get_d3_round_name(match)

    if side is None:
        upper_side = []
        layout['winners'] = upper_side
        lower_side = []
        layout['competitors'] = lower_side
    else:
        upper_side = lower_side = layout[side] = []

    upper_competitor = __get_upper_competitor(match, matches_by_round)
    if upper_competitor:
        upper_side.append(__get_d3_bracket_layout(
                upper_competitor, matches_by_round, 'winners'))
    else:
        blue_team_str = 'bye'
        if match.blue_team:
            blue_team_str = match.blue_team.team.short_str()
        upper_side.append({'name': blue_team_str})

    lower_competitor = __get_lower_competitor(
            match, matches_by_round)
    if lower_competitor:
        lower_side.append(__get_d3_bracket_layout(
                lower_competitor, matches_by_round, 'competitors'))
    else:
        red_team_str = 'bye'
        if match.red_team:
            red_team_str = match.red_team.team.short_str()
        lower_side.append({'name': red_team_str})

    return layout

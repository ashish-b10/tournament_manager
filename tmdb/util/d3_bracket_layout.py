from collections import OrderedDict

__all__ = ['d3_bracket_layout']

def d3_bracket_layout(tournament_division, matches_by_round):
    if not matches_by_round:
        return {}
    if (0,0,) not in matches_by_round:
        return None
    root_match = matches_by_round[(0,0,)]
    max_round_slot = max((m[0] for m in matches_by_round.keys()))
    return __get_d3_bracket_layout(root_match, matches_by_round, max_round_slot)

def __get_upper_competitor(match, matches_by_round):
    return matches_by_round.get((
            match.round_num + 1, match.round_slot * 2,))

def __get_lower_competitor(match, matches_by_round):
    return matches_by_round.get((
            match.round_num + 1, match.round_slot * 2 + 1,))

def __get_d3_bracket_layout(match, matches_by_round, max_round_slot):
    layout = {}
    layout['text'] = OrderedDict()
    layout['text']['name'] = "" 
    if match.winning_team:
        layout['text']['name'] = match.winning_team.short_str()

    layout['text']['desc'] = str(match)
    children = []

    upper_child = __get_upper_competitor(match, matches_by_round)
    if upper_child:
        children.append(__get_d3_bracket_layout(upper_child, matches_by_round, max_round_slot))
    else:
        new_child = {
            "text": OrderedDict()
        }
        if match.blue_team:
            new_child['text']['name'] = match.blue_team.team.short_str()
            if match.round_num == max_round_slot:
                new_child['HTMLclass'] = "first-draw"
            else:
                new_child['text']['desc'] = ""
        else:
            new_child['text']['name'] = 'Bye'
        children.append(new_child)

    lower_child = __get_lower_competitor(match, matches_by_round)
    if lower_child:
        children.append(__get_d3_bracket_layout(lower_child, matches_by_round, max_round_slot))
    else:
        new_child = {
            "text": OrderedDict()
        }
        if match.red_team:
            new_child['text']['name'] = match.red_team.team.short_str()
            if match.round_num == max_round_slot:
                new_child['HTMLclass'] = "first-draw"
            else:
                new_child['text']['desc'] = ""
        else:
            new_child['text']['name'] = 'Bye'
        children.append(new_child)
    layout['children'] = children

    return layout

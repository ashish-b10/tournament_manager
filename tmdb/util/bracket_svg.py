#!/usr/bin/env python3

import xml.etree.ElementTree as et

class BracketException(Exception): pass

class SvgBracket():
    font_size = "8pt"
    font_family = "sans-serif"
    height = "9.75in"
    width = "7.5in"
    line_width = 4
    line_color = "black"
    team_name_horiz_padding = 3

    def __init__(self, blue_team_text=None, red_team_text=None):
        if blue_team_text is None:
            blue_team_text = lambda match: match.blue_team_text
        self.blue_team_text = blue_team_text

        if red_team_text is None:
            red_team_text = lambda match: match.red_team_text
        self.red_team_text = red_team_text

        self.root = et.Element("svg")
        self.root.set("xmlns", "http://www.w3.org/2000/svg")
        self.root.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
        self.root.set("width", SvgBracket.width)
        self.root.set("height", SvgBracket.height)

    @staticmethod
    def create(teams, *args, **kwargs):
        bracket = SvgBracket(*args, **kwargs)
        bracket.__create_rounds(teams)
        return bracket

    def __create_rounds(self, teams):
        num_rounds = len(teams)
        width = 100 / num_rounds
        for round_num, round_matches in enumerate(teams):
            attrib = {
                    "x": str(round_num * width) + "%",
                    "width": str(width) + "%",
            }
            round_num = num_rounds - 1 - round_num
            round_element = et.SubElement(self.root, "svg", attrib)
            self.__create_round(round_element, round_num, round_matches)

    def __create_round(self, round_element, round_num, round_matches):
        num_matches = len(round_matches)
        height = 100 / num_matches
        for round_match_num, round_match in enumerate(round_matches):
            attrib = {
                "y": str(round_match_num * height) + "%",
                "height": str(height) + "%",
            }
            match_element = et.SubElement(round_element, "svg", attrib)
            if round_match is None:
                continue
            cell_type = "lower" if round_match_num % 2 else "upper"
            if round_num == 0: cell_type = "final"
            self.__create_match(match_element, cell_type, round_match)

    def __create_match(self, match_element, cell_type, round_match):
        valid_cell_types = ("lower", "upper", "final")
        if not cell_type in valid_cell_types:
            raise BracketException("Invalid cell_type %s, must be one of %s" %(
                    cell_type, valid_cell_types))

        attrib = {
            "stroke": SvgBracket.line_color,
            "stroke-width": str(SvgBracket.line_width/2),
            "x1": "0%",
            "y1": "50%",
            "x2": "100%",
            "y2": "50%",
        }
        et.SubElement(match_element, "line", dict(attrib))
        if cell_type == "lower":
            attrib["stroke-width"] = str(SvgBracket.line_width)
            attrib["x1"] = "100%"
            attrib["y1"] = "50%"
            attrib["x2"] = "100%"
            attrib["y2"] = "0%"
            et.SubElement(match_element, "line", dict(attrib))

        if cell_type == "upper":
            attrib["stroke-width"] = str(SvgBracket.line_width)
            attrib["x1"] = "100%"
            attrib["y1"] = "50%"
            attrib["x2"] = "100%"
            attrib["y2"] = "100%"
            et.SubElement(match_element, "line", dict(attrib))

        text_attrib = SvgBracket.__font_attrib()
        text_attrib["x"] = str(SvgBracket.team_name_horiz_padding) + "px"
        text_attrib["y"] = "50%"
        text_attrib["style"] = "dominant-baseline: text-before-edge"
        text_elem = et.SubElement(match_element, "text", attrib = text_attrib)

        blue_team = self.blue_team_text(round_match)
        attrib = {"x": "0", "dy": "-1.5em", "fill": "rgb(0,0,200)"}
        if not blue_team:
            blue_team = '.'
            attrib['fill-opacity'] = '0.1'
        et.SubElement(text_elem, "tspan", attrib=attrib).text = blue_team

        red_team = self.red_team_text(round_match)
        attrib = {"x": "0", "dy": "1.5em", "fill": "rgb(200,0,0)"}
        if not blue_team:
            red_team = '.'
            attrib['fill-opacity'] = '0'
        et.SubElement(text_elem, "tspan", attrib=attrib).text = red_team

    def tostring(self, *args, **kwargs):
        return et.tostring(self.root, *args, **kwargs)

    @staticmethod
    def __font_attrib():
        return {
                "font-family": SvgBracket.font_family,
                "font-size": SvgBracket.font_size,
        }

if __name__ == "__main__":
    teams = [[['[55] blue_team', '[55] red_team']] * (2**i) for i in range(6)]
    teams[5][10] = None
    teams[5][11] = None
    teams[4][5] = None
    teams = list(reversed(teams))
    blue_team_text = lambda match: match[0]
    red_team_text = lambda match: match[1]
    bracket = SvgBracket.create(teams, blue_team_text=blue_team_text,
            red_team_text=red_team_text)
    with open("bracket_generated.svg", "wb") as fh:
        fh.write(b"<html><body>")
        et.ElementTree(element=bracket.root).write(fh, encoding="utf-8")
        fh.write(b"</body></html>")

#!/usr/bin/env python3
from django.core.management.base import BaseCommand
from tmdb import models
import shutil
import os

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from pdfrw import PdfReader, PdfWriter, PageMerge

def create_match_sheet(match_num, blue_team=None, red_team=None, male=False,
        female=False, a_team=False, b_team=False, c_team=False):
    teams_canvas = canvas.Canvas("teams.pdf", pagesize=letter)
    teams_canvas.setLineWidth(3)
    xoffset, yoffset = 0, 0
    if male:
        teams_canvas.ellipse(
                3.2*inch + xoffset, 9.5*inch + yoffset,
                2.4*inch + xoffset, 9.1*inch + yoffset)
    xoffset = 4.23 * inch
    if female:
        teams_canvas.ellipse(
                3.2*inch + xoffset, 9.5*inch + yoffset,
                2.4*inch + xoffset, 9.1*inch + yoffset)
    yoffset = -.3 * inch
    if c_team:
        teams_canvas.ellipse(
                3.2*inch + xoffset, 9.5*inch + yoffset,
                2.4*inch + xoffset, 9.1*inch + yoffset)
    xoffset = 0
    if a_team:
        teams_canvas.ellipse(
                3.2*inch + xoffset, 9.5*inch + yoffset,
                2.4*inch + xoffset, 9.1*inch + yoffset)
    xoffset = 4.23/ 2 * inch
    if b_team:
        teams_canvas.ellipse(
                3.2*inch + xoffset, 9.5*inch + yoffset,
                2.4*inch + xoffset, 9.1*inch + yoffset)
    teams_canvas.setFont('Helvetica', 24)
    teams_canvas.drawString(1.7*inch, 7.8*inch, str(match_num))
    teams_canvas.setFont('Helvetica', 18)
    if blue_team:
        teams_canvas.drawString(.65*inch, 6.65*inch, blue_team)
    xoffset = 3.75*inch
    if red_team:
        teams_canvas.drawString(.65*inch + xoffset, 6.65*inch, red_team)
    teams_canvas.save()

    match_sheet_fn = '/home/user/dev/match_sheet/match_sheet.pdf'
    teams_fn = 'teams.pdf'
    output_fn = os.path.join(match_sheet_dir, 'match_%d.pdf' %(match_num))
    output_canvas = PageMerge().add(PdfReader(match_sheet_fn).pages[0])[0]
    trailer = PdfReader(teams_fn)

    for page in trailer.pages:
        PageMerge(page).add(output_canvas, prepend=True).render()
    PdfWriter().write(output_fn, trailer)
    return output_fn

def combine_match_sheets(match_sheets):
    output_fn = os.path.join(match_sheet_dir,'combined_match_sheets.pdf')
    writer = PdfWriter()
    for match_sheet in match_sheets:
        writer.addpages(PdfReader(match_sheet).pages)

    writer.write(output_fn)
    return output_fn

match_sheet_dir = '/dev/shm/match_sheets'

def create_match_sheets():
    tournament = models.Tournament.objects.get(location="Princeton")
    matches = models.TeamMatch.objects.filter(division__tournament = tournament)
    match_sheets = []
    if not os.path.exists(match_sheet_dir):
        os.mkdir(match_sheet_dir)
    shutil.rmtree('/dev/shm/match_sheets')
    os.mkdir(match_sheet_dir)

    for match in matches:
        match_num = match.number + 1
        blue_team = red_team = None
        if match.blue_team:
            blue_team = str(match.blue_team.team)
        if match.red_team:
            red_team = str(match.red_team.team)
        if not blue_team and not red_team:
            continue
        male = match.division.division.sex == 1
        female = match.division.division.sex == 0
        a_team = match.division.division.skill_level == 0
        b_team = match.division.division.skill_level == 1
        c_team = match.division.division.skill_level == 2
        match_sheet = create_match_sheet(match_num, blue_team=blue_team,
                red_team=red_team, male=male, female=female, a_team=a_team,
                b_team=b_team, c_team=c_team)
        match_sheets.append(match_sheet)
    return combine_match_sheets(match_sheets)

class Command(BaseCommand):
    help = 'Creates match sheets for a tournament'

    def handle(self, *args, **options):
        create_match_sheets()

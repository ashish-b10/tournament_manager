import os
from io import BytesIO, StringIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from PyPDF2 import PdfFileReader, PdfFileWriter

from tmdb import models

__all__ = ["create_match_sheets"]

def _get_round_str(round_num):
    if round_num == 0:
        return "Finals"
    if round_num == 1:
        return "Semi-Finals"
    if round_num == 2:
        return "Quarter-Finals"
    return "Round of %d" %(2**(round_num+1),)

def _get_match_sheet_template_fn():
    this_directory = os.path.dirname(__file__)
    return os.path.join(this_directory, 'match_sheet.pdf')

def _draw_ellipse(drawing_canvas, xoffset, yoffset):
    drawing_canvas.ellipse(
            3.2*inch + xoffset, 9.5*inch + yoffset,
            2.4*inch + xoffset, 9.1*inch + yoffset)

def _draw_match_sheet(match, female=False, a_team=False, b_team=False, c_team=False):
    drawing_layer = StringIO()
    drawing_canvas = canvas.Canvas(drawing_layer, pagesize=letter)
    drawing_canvas.setLineWidth(3)
    xoffset, yoffset = 0, .1*inch
    if match.division.division.sex == models.SexField.MALE:
        _draw_ellipse(drawing_canvas, xoffset, yoffset)
    xoffset = 4.23 * inch
    if match.division.division.sex == models.SexField.FEMALE:
        _draw_ellipse(drawing_canvas, xoffset, yoffset)
    yoffset = -.23 * inch
    skill_level = match.division.division.skill_level
    if skill_level == models.DivisionLevelField.C_TEAM_VAL:
        _draw_ellipse(drawing_canvas, xoffset, yoffset)
    xoffset = 0
    if skill_level == models.DivisionLevelField.A_TEAM_VAL:
        _draw_ellipse(drawing_canvas, xoffset, yoffset)
    xoffset = 4.23/ 2 * inch
    if skill_level == models.DivisionLevelField.B_TEAM_VAL:
        _draw_ellipse(drawing_canvas, xoffset, yoffset)
    drawing_canvas.setFont('Helvetica', 24)
    xoffset = 1.8 * inch
    yoffset = 8.23 * inch
    drawing_canvas.drawString(xoffset, yoffset, str(match.number))
    if match.ring_number:
        drawing_canvas.drawString(xoffset + 3.65 * inch, yoffset,
            str(match.ring_number))
    drawing_canvas.drawString(6.3*inch, 10.4*inch,
            _get_round_str(match.round_num))
    drawing_canvas.setFont('Helvetica', 18)
    xoffset = .65 * inch
    yoffset = 7.25 * inch
    if match.blue_team:
        drawing_canvas.drawString(xoffset, yoffset,
                str(match.blue_team))
    if match.red_team:
        drawing_canvas.drawString(xoffset + 3.75*inch, yoffset,
                str(match.red_team))

    return PdfFileReader(BytesIO(drawing_canvas.getpdfdata())).getPage(0)

def _get_match_sheet_base_layer():
    match_sheet_fn = _get_match_sheet_template_fn()
    return PdfFileReader(match_sheet_fn).getPage(0)

def create_match_sheets(matches):
    output_pdf = PdfFileWriter()

    for match in matches:
        match_sheet_base_layer = _get_match_sheet_base_layer()
        match_sheet_base_layer.mergePage(_draw_match_sheet(match))
        output_pdf.addPage(match_sheet_base_layer)

    output_stream = BytesIO()
    output_pdf.write(output_stream)
    output_stream.flush()
    output_stream.seek(0)
    return output_stream

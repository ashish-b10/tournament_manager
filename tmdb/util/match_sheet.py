import os
from io import BytesIO, StringIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from PyPDF2 import PdfFileReader, PdfFileWriter

from tmdb import models

__all__ = ["create_match_sheets"]

def _get_match_sheet_template_fn():
    this_directory = os.path.dirname(__file__)
    return os.path.join(this_directory, 'match_sheet.pdf')

def _draw_match_sheet(match, female=False, a_team=False, b_team=False, c_team=False):
    drawing_layer = StringIO()
    drawing_canvas = canvas.Canvas(drawing_layer, pagesize=letter)
    drawing_canvas.setLineWidth(3)
    xoffset, yoffset = 0, 0
    if match.division.division.sex == models.SexEnum.M:
        drawing_canvas.ellipse(
                3.2*inch + xoffset, 9.5*inch + yoffset,
                2.4*inch + xoffset, 9.1*inch + yoffset)
    xoffset = 4.23 * inch
    if match.division.division.sex == models.SexEnum.F:
        drawing_canvas.ellipse(
                3.2*inch + xoffset, 9.5*inch + yoffset,
                2.4*inch + xoffset, 9.1*inch + yoffset)
    yoffset = -.3 * inch
    if match.division.division.skill_level == models.DivisionLevelEnum.C:
        drawing_canvas.ellipse(
                3.2*inch + xoffset, 9.5*inch + yoffset,
                2.4*inch + xoffset, 9.1*inch + yoffset)
    xoffset = 0
    if match.division.division.skill_level == models.DivisionLevelEnum.A:
        drawing_canvas.ellipse(
                3.2*inch + xoffset, 9.5*inch + yoffset,
                2.4*inch + xoffset, 9.1*inch + yoffset)
    xoffset = 4.23/ 2 * inch
    if match.division.division.skill_level == models.DivisionLevelEnum.B:
        drawing_canvas.ellipse(
                3.2*inch + xoffset, 9.5*inch + yoffset,
                2.4*inch + xoffset, 9.1*inch + yoffset)
    drawing_canvas.setFont('Helvetica', 24)
    drawing_canvas.drawString(1.7*inch, 7.8*inch, str(match.number))
    drawing_canvas.setFont('Helvetica', 18)
    if match.blue_team:
        drawing_canvas.drawString(.65*inch, 6.65*inch,
                str(match.blue_team))
    xoffset = 3.75*inch
    if match.red_team:
        drawing_canvas.drawString(.65*inch + xoffset, 6.65*inch,
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

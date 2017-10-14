import os
from io import BytesIO, StringIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import units
from PyPDF2 import PdfFileReader, PdfFileWriter

bracket_32_rounds = {
    'round_4_left_x': 0.9,
    'round_3_left_x': 4.25,
    'round_2_left_x': 7,
    'round_1_left_x': 9.5,
    'round_0_left_x': 10.5,
    'round_0_right_x': 14.5,
    'round_1_right_x': 18.25,
    'round_2_right_x': 20.75,
    'round_3_right_x': 23.7,
    'round_4_right_x': 27
    }

match_positions_32 = {
    (0, 0, 'blue'): (bracket_32_rounds['round_0_left_x'], 10.9, 'blue'),

    (0, 0, 'red'): (bracket_32_rounds['round_0_right_x'], 10.9, 'red'),

    (1,  0, 'blue'): (bracket_32_rounds['round_1_left_x'], 16, 'blue'),
    (1,  0, 'red'): (bracket_32_rounds['round_1_left_x'], 6.2, 'red'),

    (1,  1, 'blue'): (bracket_32_rounds['round_1_right_x'], 6.2, 'blue'),
    (1,  1, 'red'): (bracket_32_rounds['round_1_right_x'], 16, 'red'),

    (2,  0, 'blue'): (bracket_32_rounds['round_2_left_x'], 18.275, 'blue'),
    (2,  0, 'red'): (bracket_32_rounds['round_2_left_x'], 13.45, 'red'),
    (2,  1, 'blue'): (bracket_32_rounds['round_2_left_x'], 8.6, 'blue'),
    (2,  1, 'red'): (bracket_32_rounds['round_2_left_x'], 3.75, 'red'),

    (2,  2, 'blue'): (bracket_32_rounds['round_2_right_x'], 3.75, 'blue'),
    (2,  2, 'red'): (bracket_32_rounds['round_2_right_x'], 8.6, 'red'),
    (2,  3, 'blue'): (bracket_32_rounds['round_2_right_x'], 13.45, 'blue'),
    (2,  3, 'red'): (bracket_32_rounds['round_2_right_x'], 18.275, 'red'),

    (3,  0, 'blue'): (bracket_32_rounds['round_3_left_x'], 19.525, 'blue'),
    (3,  0, 'red'): (bracket_32_rounds['round_3_left_x'], 17.025, 'red'),
    (3,  1, 'blue'): (bracket_32_rounds['round_3_left_x'], 14.625, 'blue'),
    (3,  1, 'red'): (bracket_32_rounds['round_3_left_x'], 12.125, 'red'),
    (3,  2, 'blue'): (bracket_32_rounds['round_3_left_x'], 9.8, 'blue'),
    (3,  2, 'red'): (bracket_32_rounds['round_3_left_x'], 7.3, 'red'),
    (3,  3, 'blue'): (bracket_32_rounds['round_3_left_x'], 4.9, 'blue'),
    (3,  3, 'red'): (bracket_32_rounds['round_3_left_x'], 2.4, 'red'),

    (3,  4, 'blue'): (bracket_32_rounds['round_3_right_x'], 2.4, 'blue'),
    (3,  4, 'red'): (bracket_32_rounds['round_3_right_x'], 4.9, 'red'),
    (3,  5, 'blue'): (bracket_32_rounds['round_3_right_x'], 7.3, 'blue'),
    (3,  5, 'red'): (bracket_32_rounds['round_3_right_x'], 9.8, 'red'),
    (3,  6, 'blue'): (bracket_32_rounds['round_3_right_x'], 12.125, 'blue'),
    (3,  6, 'red'): (bracket_32_rounds['round_3_right_x'], 14.625, 'red'),
    (3,  7, 'blue'): (bracket_32_rounds['round_3_right_x'], 17.025, 'blue'),
    (3,  7, 'red'): (bracket_32_rounds['round_3_right_x'], 19.525, 'red'),

    (4,  0, 'blue'): (bracket_32_rounds['round_4_left_x'], 20.15, 'blue'),
    (4,  0, 'red'): (bracket_32_rounds['round_4_left_x'], 18.9, 'red'),
    (4,  1, 'blue'): (bracket_32_rounds['round_4_left_x'], 17.65, 'blue'),
    (4,  1, 'red'): (bracket_32_rounds['round_4_left_x'], 16.4, 'red'),
    (4,  2, 'blue'): (bracket_32_rounds['round_4_left_x'], 15.21, 'blue'),
    (4,  2, 'red'): (bracket_32_rounds['round_4_left_x'], 13.95, 'red'),
    (4,  3, 'blue'): (bracket_32_rounds['round_4_left_x'], 12.75, 'blue'),
    (4,  3, 'red'): (bracket_32_rounds['round_4_left_x'], 11.55, 'red'),
    (4,  4, 'blue'): (bracket_32_rounds['round_4_left_x'], 10.35, 'blue'),
    (4,  4, 'red'): (bracket_32_rounds['round_4_left_x'], 9.1, 'red'),
    (4,  5, 'blue'): (bracket_32_rounds['round_4_left_x'], 7.95, 'blue'),
    (4,  5, 'red'): (bracket_32_rounds['round_4_left_x'], 6.7, 'red'),
    (4,  6, 'blue'): (bracket_32_rounds['round_4_left_x'], 5.53, 'blue'),
    (4,  6, 'red'): (bracket_32_rounds['round_4_left_x'], 4.25, 'red'),
    (4,  7, 'blue'): (bracket_32_rounds['round_4_left_x'], 3.1, 'blue'),
    (4,  7, 'red'): (bracket_32_rounds['round_4_left_x'], 1.8, 'red'),

    (4,  8, 'blue'): (bracket_32_rounds['round_4_right_x'], 1.8, 'blue'),
    (4,  8, 'red'): (bracket_32_rounds['round_4_right_x'], 3.1, 'red'),
    (4,  9, 'blue'): (bracket_32_rounds['round_4_right_x'], 4.25, 'blue'),
    (4,  9, 'red'): (bracket_32_rounds['round_4_right_x'], 5.53, 'red'),
    (4, 10, 'blue'): (bracket_32_rounds['round_4_right_x'], 6.7, 'blue'),
    (4, 10, 'red'): (bracket_32_rounds['round_4_right_x'], 7.95, 'red'),
    (4, 11, 'blue'): (bracket_32_rounds['round_4_right_x'], 9.1, 'blue'),
    (4, 11, 'red'): (bracket_32_rounds['round_4_right_x'], 10.35, 'red'),
    (4, 12, 'blue'): (bracket_32_rounds['round_4_right_x'], 11.55, 'blue'),
    (4, 12, 'red'): (bracket_32_rounds['round_4_right_x'], 12.75, 'red'),
    (4, 13, 'blue'): (bracket_32_rounds['round_4_right_x'], 13.95, 'blue'),
    (4, 13, 'red'): (bracket_32_rounds['round_4_right_x'], 15.21, 'red'),
    (4, 14, 'blue'): (bracket_32_rounds['round_4_right_x'], 16.4, 'blue'),
    (4, 14, 'red'): (bracket_32_rounds['round_4_right_x'], 17.65, 'red'),
    (4, 15, 'blue'): (bracket_32_rounds['round_4_right_x'], 18.9, 'blue'),
    (4, 15, 'red'): (bracket_32_rounds['round_4_right_x'], 20.15, 'red'),
}

match_positions_64 = {
    # (0, 0, 'blue'): (0, 0, 'blue'),
    # (0, 0, 'red'): (0, 0, 'red'),
    # (1,  0, 'blue'): (1,  0, 'blue'),
    # (1,  0, 'red'): (1,  0, 'red'),
    # (1,  1, 'blue'): (1,  1, 'blue'),
    # (1,  1, 'red'): (1,  1, 'red'),
    # (2,  0, 'blue'): (2,  0, 'blue'),
    # (2,  0, 'red'): (2,  0, 'red'),
    # (2,  1, 'blue'): (2,  1, 'blue'),
    # (2,  1, 'red'): (2,  1, 'red'),
    # (2,  2, 'blue'): (2,  2, 'blue'),
    # (2,  2, 'red'): (2,  2, 'red'),
    # (2,  3, 'blue'): (2,  3, 'blue'),
    # (2,  3, 'red'): (2,  3, 'red'),
    # (3,  0, 'blue'): (3,  0, 'blue'),
    # (3,  0, 'red'): (3,  0, 'red'),
    # (3,  1, 'blue'): (3,  1, 'blue'),
    # (3,  1, 'red'): (3,  1, 'red'),
    # (3,  2, 'blue'): (3,  2, 'blue'),
    # (3,  2, 'red'): (3,  2, 'red'),
    # (3,  3, 'blue'): (3,  3, 'blue'),
    # (3,  3, 'red'): (3,  3, 'red'),
    # (3,  4, 'blue'): (3,  4, 'blue'),
    # (3,  4, 'red'): (3,  4, 'red'),
    # (3,  5, 'blue'): (3,  5, 'blue'),
    # (3,  5, 'red'): (3,  5, 'red'),
    # (3,  6, 'blue'): (3,  6, 'blue'),
    # (3,  6, 'red'): (3,  6, 'red'),
    # (3,  7, 'blue'): (3,  7, 'blue'),
    # (3,  7, 'red'): (3,  7, 'red'),
    # (4,  0, 'blue'): (4,  0, 'blue'),
    # (4,  0, 'red'): (4,  0, 'red'),
    # (4,  1, 'blue'): (4,  1, 'blue'),
    # (4,  1, 'red'): (4,  1, 'red'),
    # (4,  2, 'blue'): (4,  2, 'blue'),
    # (4,  2, 'red'): (4,  2, 'red'),
    # (4,  3, 'blue'): (4,  3, 'blue'),
    # (4,  3, 'red'): (4,  3, 'red'),
    # (4,  4, 'blue'): (4,  4, 'blue'),
    # (4,  4, 'red'): (4,  4, 'red'),
    # (4,  5, 'blue'): (4,  5, 'blue'),
    # (4,  5, 'red'): (4,  5, 'red'),
    # (4,  6, 'blue'): (4,  6, 'blue'),
    # (4,  6, 'red'): (4,  6, 'red'),
    # (4,  7, 'blue'): (4,  7, 'blue'),
    # (4,  7, 'red'): (4,  7, 'red'),
    # (4,  8, 'blue'): (4,  8, 'blue'),
    # (4,  8, 'red'): (4,  8, 'red'),
    # (4,  9, 'blue'): (4,  9, 'blue'),
    # (4,  9, 'red'): (4,  9, 'red'),
    # (4, 10, 'blue'): (4, 10, 'blue'),
    # (4, 10, 'red'): (4, 10, 'red'),
    # (4, 11, 'blue'): (4, 11, 'blue'),
    # (4, 11, 'red'): (4, 11, 'red'),
    # (4, 12, 'blue'): (4, 12, 'blue'),
    # (4, 12, 'red'): (4, 12, 'red'),
    # (4, 13, 'blue'): (4, 13, 'blue'),
    # (4, 13, 'red'): (4, 13, 'red'),
    # (4, 14, 'blue'): (4, 14, 'blue'),
    # (4, 14, 'red'): (4, 14, 'red'),
    # (4, 15, 'blue'): (4, 15, 'blue'),
    # (4, 15, 'red'): (4, 15, 'red'),
    (5,  0, 'blue'): (5,  0, 'blue'),
    (5,  0, 'red'): (5,  0, 'red'),
    (5,  1, 'blue'): (5,  1, 'blue'),
    (5,  1, 'red'): (5,  1, 'red'),
    (5,  2, 'blue'): (5,  2, 'blue'),
    (5,  2, 'red'): (5,  2, 'red'),
    (5,  3, 'blue'): (5,  3, 'blue'),
    (5,  3, 'red'): (5,  3, 'red'),
    (5,  4, 'blue'): (5,  4, 'blue'),
    (5,  4, 'red'): (5,  4, 'red'),
    (5,  5, 'blue'): (5,  5, 'blue'),
    (5,  5, 'red'): (5,  5, 'red'),
    (5,  6, 'blue'): (5,  6, 'blue'),
    (5,  6, 'red'): (5,  6, 'red'),
    (5,  7, 'blue'): (5,  7, 'blue'),
    (5,  7, 'red'): (5,  7, 'red'),
    (5,  8, 'blue'): (5,  8, 'blue'),
    (5,  8, 'red'): (5,  8, 'red'),
    (5,  9, 'blue'): (5,  9, 'blue'),
    (5,  9, 'red'): (5,  9, 'red'),
    (5, 10, 'blue'): (5, 10, 'blue'),
    (5, 10, 'red'): (5, 10, 'red'),
    (5, 11, 'blue'): (5, 11, 'blue'),
    (5, 11, 'red'): (5, 11, 'red'),
    (5, 12, 'blue'): (5, 12, 'blue'),
    (5, 12, 'red'): (5, 12, 'red'),
    (5, 13, 'blue'): (5, 13, 'blue'),
    (5, 13, 'red'): (5, 13, 'red'),
    (5, 14, 'blue'): (5, 14, 'blue'),
    (5, 14, 'red'): (5, 14, 'red'),
    (5, 15, 'blue'): (5, 15, 'blue'),
    (5, 15, 'red'): (5, 15, 'red'),
    (5, 16, 'blue'): (5, 16, 'blue'),
    (5, 16, 'red'): (5, 16, 'red'),
    (5, 17, 'blue'): (5, 17, 'blue'),
    (5, 17, 'red'): (5, 17, 'red'),
    (5, 18, 'blue'): (5, 18, 'blue'),
    (5, 18, 'red'): (5, 18, 'red'),
    (5, 19, 'blue'): (5, 19, 'blue'),
    (5, 19, 'red'): (5, 19, 'red'),
    (5, 20, 'blue'): (5, 20, 'blue'),
    (5, 20, 'red'): (5, 20, 'red'),
    (5, 21, 'blue'): (5, 21, 'blue'),
    (5, 21, 'red'): (5, 21, 'red'),
    (5, 22, 'blue'): (5, 22, 'blue'),
    (5, 22, 'red'): (5, 22, 'red'),
    (5, 23, 'blue'): (5, 23, 'blue'),
    (5, 23, 'red'): (5, 23, 'red'),
    (5, 24, 'blue'): (5, 24, 'blue'),
    (5, 24, 'red'): (5, 24, 'red'),
    (5, 25, 'blue'): (5, 25, 'blue'),
    (5, 25, 'red'): (5, 25, 'red'),
    (5, 26, 'blue'): (5, 26, 'blue'),
    (5, 26, 'red'): (5, 26, 'red'),
    (5, 27, 'blue'): (5, 27, 'blue'),
    (5, 27, 'red'): (5, 27, 'red'),
    (5, 28, 'blue'): (5, 28, 'blue'),
    (5, 28, 'red'): (5, 28, 'red'),
    (5, 29, 'blue'): (5, 29, 'blue'),
    (5, 29, 'red'): (5, 29, 'red'),
    (5, 30, 'blue'): (5, 30, 'blue'),
    (5, 30, 'red'): (5, 30, 'red'),
    (5, 31, 'blue'): (5, 31, 'blue'),
    (5, 31, 'red'): (5, 31, 'red'),
}

def _draw_text(drawing_canvas, position, text, right_align=False):
    print(text)
    x, y, color = position
    drawing_canvas.setFillColor(color)
    if right_align:
        drawing_canvas.drawRightString(x*units.cm, y*units.cm, text)
    else:
        drawing_canvas.drawString(x*units.cm, y*units.cm, text)

def _draw_match(match, match_positions):
    drawing_layer = StringIO()
    drawing_canvas = canvas.Canvas(drawing_layer, pagesize=letter)
    drawing_canvas.setFont('Helvetica', 8)
    right_align = (((2**(match.round_num-1))-1) < match.round_slot) and match.round_num > 1
    if (match.round_num == 1 and match.round_slot == 1):
        right_align = True
    if match.blue_team:
        match_positions_key = (match.round_num, match.round_slot, 'blue')
        position = match_positions[match_positions_key]
        team_text = "%s" %(str(match.blue_team),)
        _draw_text(drawing_canvas, position, team_text, right_align)
    if match.red_team:
        match_positions_key = (match.round_num, match.round_slot, 'red')
        position = match_positions[match_positions_key]
        team_text = "%s" %(str(match.red_team),)
        _draw_text(drawing_canvas, position, team_text, right_align)
    return PdfFileReader(BytesIO(drawing_canvas.getpdfdata())).getPage(0)

def _draw_title(matches):
    division = matches[0].division
    tournament = division.tournament
    title = '%s %s' %(division.__str__(), tournament.__str__())
    drawing_layer = StringIO()
    drawing_canvas = canvas.Canvas(drawing_layer, pagesize=letter)
    drawing_canvas.setFont('Helvetica-Bold', 16)
    drawing_canvas.setFillColor('white')
    drawing_canvas.rect(5*units.cm, 20*units.cm, 17*units.cm, 1.5*units.cm, stroke=0, fill=1)
    drawing_canvas.rect(5*units.cm, 0*units.cm, 17*units.cm, 1.5*units.cm, stroke=0, fill=1)
    drawing_canvas.setFillColor('black')
    drawing_canvas.drawCentredString(14*units.cm, 20*units.cm, title)
    return PdfFileReader(BytesIO(drawing_canvas.getpdfdata())).getPage(0)

def _get_template(filename):
    this_directory = os.path.dirname(__file__)
    return os.path.join(this_directory, filename)

def _draw_matches(output_pdf, matches):
    matches = list(matches)
    if len(matches) > 32:
        match_positions = match_positions_64
        base_layer_filename = _get_template('64teamsingleseeded.pdf')
    else:
        match_positions = match_positions_32
        base_layer_filename = _get_template('32teamsingleseeded.pdf')
    base_layer = PdfFileReader(base_layer_filename).getPage(0)
    base_layer.mergePage(_draw_title(matches))
    for match in matches:
        base_layer.mergePage(_draw_match(match, match_positions))
    output_pdf.addPage(base_layer)

def _draw_position(position):
    position_key, position_value = position
    num, slot, color = position_key
    drawing_layer = StringIO()
    drawing_canvas = canvas.Canvas(drawing_layer, pagesize=letter)
    drawing_canvas.setFont('Helvetica', 10)
    right_align = (((2**(num-1))-1) < slot) and num > 1
    if (num == 1 and slot == 1):
        right_align = True
    _draw_text(drawing_canvas, position_value, str(position_key), right_align)
    return PdfFileReader(BytesIO(drawing_canvas.getpdfdata())).getPage(0)

def _draw_positions(output_pdf, bracket_size):
    if bracket_size == 32:
        match_positions = match_positions_32
        base_layer_filename = _get_template('32teamsingleseeded.pdf')
    elif bracket_size == 64:
        match_positions = match_positions_64
        base_layer_filename = _get_template('64teamsingleseeded.pdf')
    else:
        raise ArgumentError('bracket_size=%d must be 32 or 64' %(bracket_size))

    base_layer = PdfFileReader(base_layer_filename).getPage(0)

    for position in match_positions.items():
        base_layer.mergePage(_draw_position(position))
    output_pdf.addPage(base_layer)

def create_bracket_pdf(matches):
    output_pdf = PdfFileWriter()

    #_draw_matches(output_pdf, matches)
    _draw_positions(output_pdf, 64)
    output_stream = BytesIO()
    output_pdf.write(output_stream)
    output_stream.flush()
    output_stream.seek(0)
    return output_stream

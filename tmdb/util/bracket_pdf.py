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
bracket_32_positions = {
    (0, 0, 'winning_team'): (14, 1, 'black'),

    (0, 0, 'blue'): (bracket_32_rounds['round_0_left_x'], 10.9, 'blue'),

    (0, 0, 'red'): (bracket_32_rounds['round_0_right_x'], 10.9, 'red'),

    (1,  0, 'blue'): (bracket_32_rounds['round_1_left_x'], 16, 'blue'),
    (1,  0, 'red'): (bracket_32_rounds['round_1_left_x'], 6.2, 'red'),

    (1,  1, 'blue'): (bracket_32_rounds['round_1_right_x'], 16, 'blue'),
    (1,  1, 'red'): (bracket_32_rounds['round_1_right_x'], 6.2, 'red'),

    (2,  0, 'blue'): (bracket_32_rounds['round_2_left_x'], 18.275, 'blue'),
    (2,  0, 'red'): (bracket_32_rounds['round_2_left_x'], 13.45, 'red'),
    (2,  1, 'blue'): (bracket_32_rounds['round_2_left_x'], 8.6, 'blue'),
    (2,  1, 'red'): (bracket_32_rounds['round_2_left_x'], 3.75, 'red'),

    (2,  2, 'blue'): (bracket_32_rounds['round_2_right_x'], 18.275, 'blue'),
    (2,  2, 'red'): (bracket_32_rounds['round_2_right_x'], 13.45, 'red'),
    (2,  3, 'blue'): (bracket_32_rounds['round_2_right_x'], 8.6, 'blue'),
    (2,  3, 'red'): (bracket_32_rounds['round_2_right_x'], 3.75, 'red'),

    (3,  0, 'blue'): (bracket_32_rounds['round_3_left_x'], 19.525, 'blue'),
    (3,  0, 'red'): (bracket_32_rounds['round_3_left_x'], 17.025, 'red'),
    (3,  1, 'blue'): (bracket_32_rounds['round_3_left_x'], 14.625, 'blue'),
    (3,  1, 'red'): (bracket_32_rounds['round_3_left_x'], 12.125, 'red'),
    (3,  2, 'blue'): (bracket_32_rounds['round_3_left_x'], 9.8, 'blue'),
    (3,  2, 'red'): (bracket_32_rounds['round_3_left_x'], 7.3, 'red'),
    (3,  3, 'blue'): (bracket_32_rounds['round_3_left_x'], 4.9, 'blue'),
    (3,  3, 'red'): (bracket_32_rounds['round_3_left_x'], 2.4, 'red'),

    (3,  4, 'blue'): (bracket_32_rounds['round_3_right_x'], 19.525, 'blue'),
    (3,  4, 'red'): (bracket_32_rounds['round_3_right_x'], 17.025, 'red'),
    (3,  5, 'blue'): (bracket_32_rounds['round_3_right_x'], 14.625, 'blue'),
    (3,  5, 'red'): (bracket_32_rounds['round_3_right_x'], 12.125, 'red'),
    (3,  6, 'blue'): (bracket_32_rounds['round_3_right_x'], 9.8, 'blue'),
    (3,  6, 'red'): (bracket_32_rounds['round_3_right_x'], 7.3, 'red'),
    (3,  7, 'blue'): (bracket_32_rounds['round_3_right_x'], 4.9, 'blue'),
    (3,  7, 'red'): (bracket_32_rounds['round_3_right_x'], 2.4, 'red'),

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

    (4,  8, 'blue'): (bracket_32_rounds['round_4_right_x'], 20.15, 'blue'),
    (4,  8, 'red'): (bracket_32_rounds['round_4_right_x'], 18.9, 'red'),
    (4,  9, 'blue'): (bracket_32_rounds['round_4_right_x'], 17.65, 'blue'),
    (4,  9, 'red'): (bracket_32_rounds['round_4_right_x'], 16.4, 'red'),
    (4, 10, 'blue'): (bracket_32_rounds['round_4_right_x'], 15.21, 'blue'),
    (4, 10, 'red'): (bracket_32_rounds['round_4_right_x'], 13.95, 'red'),
    (4, 11, 'blue'): (bracket_32_rounds['round_4_right_x'], 12.75, 'blue'),
    (4, 11, 'red'): (bracket_32_rounds['round_4_right_x'], 11.55, 'red'),
    (4, 12, 'blue'): (bracket_32_rounds['round_4_right_x'], 10.35, 'blue'),
    (4, 12, 'red'): (bracket_32_rounds['round_4_right_x'], 9.1, 'red'),
    (4, 13, 'blue'): (bracket_32_rounds['round_4_right_x'], 7.95, 'blue'),
    (4, 13, 'red'): (bracket_32_rounds['round_4_right_x'], 6.7, 'red'),
    (4, 14, 'blue'): (bracket_32_rounds['round_4_right_x'], 5.53, 'blue'),
    (4, 14, 'red'): (bracket_32_rounds['round_4_right_x'], 4.25, 'red'),
    (4, 15, 'blue'): (bracket_32_rounds['round_4_right_x'], 3.1, 'blue'),
    (4, 15, 'red'): (bracket_32_rounds['round_4_right_x'], 1.8, 'red'),
}

bracket_64_rounds = {
    'round_5_left_x': 0.725,
    'round_4_left_x': 3.1,
    'round_3_left_x': 5.75,
    'round_2_left_x': 8.29,
    'round_1_left_x': 10.53,
    'round_0_left_x': 11.3,
    'round_0_right_x': 14.2,
    'round_1_right_x': 17.125,
    'round_2_right_x': 19.5,
    'round_3_right_x': 22,
    'round_4_right_x': 24.6,
    'round_5_right_x': 27.1
}
bracket_64_positions = {
    (0, 0, 'winning_team'): (14, 1, 'black'),

    (0, 0, 'blue'): (bracket_64_rounds['round_0_left_x'], 10.45, 'blue'),
    (0, 0, 'red'): (bracket_64_rounds['round_0_right_x'], 10.45, 'red'),

    (1,  0, 'blue'): (bracket_64_rounds['round_1_left_x'],  16.2, 'blue'),
    (1,  0, 'red'): (bracket_64_rounds['round_1_left_x'],  5.21, 'red'),

    (1,  1, 'blue'): (bracket_64_rounds['round_1_right_x'],  16.2, 'blue'),
    (1,  1, 'red'): (bracket_64_rounds['round_1_right_x'],  5.21, 'red'),

    # (1,  1, 'blue'): (bracket_64_rounds['round_1_right_x'],  5.21, 'blue'),
    # (1,  1, 'red'): (bracket_64_rounds['round_1_right_x'],  16.2, 'red'),

    (2,  0, 'blue'): (bracket_64_rounds['round_2_left_x'],  18.8, 'blue'),
    (2,  0, 'red'): (bracket_64_rounds['round_2_left_x'],  13.5, 'red'),
    (2,  1, 'blue'): (bracket_64_rounds['round_2_left_x'],  8, 'blue'),
    (2,  1, 'red'): (bracket_64_rounds['round_2_left_x'],  2.795, 'red'),

    (2,  2, 'blue'): (bracket_64_rounds['round_2_right_x'],  18.8, 'blue'),
    (2,  2, 'red'): (bracket_64_rounds['round_2_right_x'],  13.5, 'red'),
    (2,  3, 'blue'): (bracket_64_rounds['round_2_right_x'],  8, 'blue'),
    (2,  3, 'red'): (bracket_64_rounds['round_2_right_x'],  2.795, 'red'),

    # (2,  2, 'blue'): (bracket_64_rounds['round_2_right_x'],  2.795, 'blue'),
    # (2,  2, 'red'): (bracket_64_rounds['round_2_right_x'],  8, 'red'),
    # (2,  3, 'blue'): (bracket_64_rounds['round_2_right_x'],  13.5, 'blue'),
    # (2,  3, 'red'): (bracket_64_rounds['round_2_right_x'],  18.8, 'red'),

    (3,  0, 'blue'): (bracket_64_rounds['round_3_left_x'],  20.1, 'blue'),
    (3,  0, 'red'): (bracket_64_rounds['round_3_left_x'],  17.5, 'red'),
    (3,  1, 'blue'): (bracket_64_rounds['round_3_left_x'],  14.9, 'blue'),
    (3,  1, 'red'): (bracket_64_rounds['round_3_left_x'],  12.3, 'red'),
    (3,  2, 'blue'): (bracket_64_rounds['round_3_left_x'],  9.3, 'blue'),
    (3,  2, 'red'): (bracket_64_rounds['round_3_left_x'],  6.7, 'red'),
    (3,  3, 'blue'): (bracket_64_rounds['round_3_left_x'],  4.1, 'blue'),
    (3,  3, 'red'): (bracket_64_rounds['round_3_left_x'],  1.49, 'red'),

    (3,  4, 'blue'): (bracket_64_rounds['round_3_right_x'],  20.1, 'blue'),
    (3,  4, 'red'): (bracket_64_rounds['round_3_right_x'],  17.5, 'red'),
    (3,  5, 'blue'): (bracket_64_rounds['round_3_right_x'],  14.9, 'blue'),
    (3,  5, 'red'): (bracket_64_rounds['round_3_right_x'],  12.3, 'red'),
    (3,  6, 'blue'): (bracket_64_rounds['round_3_right_x'],  9.3, 'blue'),
    (3,  6, 'red'): (bracket_64_rounds['round_3_right_x'],  6.7, 'red'),
    (3,  7, 'blue'): (bracket_64_rounds['round_3_right_x'],  4.1, 'blue'),
    (3,  7, 'red'): (bracket_64_rounds['round_3_right_x'],  1.49, 'red'),

    # (3,  4, 'blue'): (bracket_64_rounds['round_3_right_x'],  1.49, 'blue'),
    # (3,  4, 'red'): (bracket_64_rounds['round_3_right_x'],  4.1, 'red'),
    # (3,  5, 'blue'): (bracket_64_rounds['round_3_right_x'],  6.7, 'blue'),
    # (3,  5, 'red'): (bracket_64_rounds['round_3_right_x'],  9.3, 'red'),
    # (3,  6, 'blue'): (bracket_64_rounds['round_3_right_x'],  12.3, 'blue'),
    # (3,  6, 'red'): (bracket_64_rounds['round_3_right_x'],  14.9, 'red'),
    # (3,  7, 'blue'): (bracket_64_rounds['round_3_right_x'],  17.5, 'blue'),
    # (3,  7, 'red'): (bracket_64_rounds['round_3_right_x'],  20.1, 'red'),

    (4,  0, 'blue'): (bracket_64_rounds['round_4_left_x'],  20.75, 'blue'),
    (4,  0, 'red'): (bracket_64_rounds['round_4_left_x'],  19.45, 'red'),
    (4,  1, 'blue'): (bracket_64_rounds['round_4_left_x'],  18.15, 'blue'),
    (4,  1, 'red'): (bracket_64_rounds['round_4_left_x'],  16.85, 'red'),
    (4,  2, 'blue'): (bracket_64_rounds['round_4_left_x'],  15.55, 'blue'),
    (4,  2, 'red'): (bracket_64_rounds['round_4_left_x'],  14.25, 'red'),
    (4,  3, 'blue'): (bracket_64_rounds['round_4_left_x'],  12.95, 'blue'),
    (4,  3, 'red'): (bracket_64_rounds['round_4_left_x'],  11.65, 'red'),
    (4,  4, 'blue'): (bracket_64_rounds['round_4_left_x'],  9.95, 'blue'),
    (4,  4, 'red'): (bracket_64_rounds['round_4_left_x'],  8.65, 'red'),
    (4,  5, 'blue'): (bracket_64_rounds['round_4_left_x'],  7.35, 'blue'),
    (4,  5, 'red'): (bracket_64_rounds['round_4_left_x'],  6.05, 'red'),
    (4,  6, 'blue'): (bracket_64_rounds['round_4_left_x'],  4.75, 'blue'),
    (4,  6, 'red'): (bracket_64_rounds['round_4_left_x'],  3.45, 'red'),
    (4,  7, 'blue'): (bracket_64_rounds['round_4_left_x'],  2.15, 'blue'),
    (4,  7, 'red'): (bracket_64_rounds['round_4_left_x'],  0.83, 'red'),

    (4,  8, 'blue'): (bracket_64_rounds['round_4_right_x'],  20.75, 'blue'),
    (4,  8, 'red'): (bracket_64_rounds['round_4_right_x'],  19.45, 'red'),
    (4,  9, 'blue'): (bracket_64_rounds['round_4_right_x'],  18.15, 'blue'),
    (4,  9, 'red'): (bracket_64_rounds['round_4_right_x'],  16.85, 'red'),
    (4,  10, 'blue'): (bracket_64_rounds['round_4_right_x'],  15.55, 'blue'),
    (4,  10, 'red'): (bracket_64_rounds['round_4_right_x'],  14.25, 'red'),
    (4,  11, 'blue'): (bracket_64_rounds['round_4_right_x'],  12.95, 'blue'),
    (4,  11, 'red'): (bracket_64_rounds['round_4_right_x'],  11.65, 'red'),
    (4,  12, 'blue'): (bracket_64_rounds['round_4_right_x'],  9.95, 'blue'),
    (4,  12, 'red'): (bracket_64_rounds['round_4_right_x'],  8.65, 'red'),
    (4,  13, 'blue'): (bracket_64_rounds['round_4_right_x'],  7.35, 'blue'),
    (4,  13, 'red'): (bracket_64_rounds['round_4_right_x'],  6.05, 'red'),
    (4,  14, 'blue'): (bracket_64_rounds['round_4_right_x'],  4.75, 'blue'),
    (4,  14, 'red'): (bracket_64_rounds['round_4_right_x'],  3.45, 'red'),
    (4,  15, 'blue'): (bracket_64_rounds['round_4_right_x'],  2.15, 'blue'),
    (4,  15, 'red'): (bracket_64_rounds['round_4_right_x'],  0.83, 'red'),

    # (4,  8, 'blue'): (bracket_64_rounds['round_4_right_x'],  0.83, 'blue'),
    # (4,  8, 'red'): (bracket_64_rounds['round_4_right_x'],  2.15, 'red'),
    # (4,  9, 'blue'): (bracket_64_rounds['round_4_right_x'],  3.45, 'blue'),
    # (4,  9, 'red'): (bracket_64_rounds['round_4_right_x'],  4.75, 'red'),
    # (4, 10, 'blue'): (bracket_64_rounds['round_4_right_x'], 6.05, 'blue'),
    # (4, 10, 'red'): (bracket_64_rounds['round_4_right_x'], 7.35, 'red'),
    # (4, 11, 'blue'): (bracket_64_rounds['round_4_right_x'], 8.65, 'blue'),
    # (4, 11, 'red'): (bracket_64_rounds['round_4_right_x'], 9.95, 'red'),
    # (4, 12, 'blue'): (bracket_64_rounds['round_4_right_x'], 11.65, 'blue'),
    # (4, 12, 'red'): (bracket_64_rounds['round_4_right_x'], 12.95, 'red'),
    # (4, 13, 'blue'): (bracket_64_rounds['round_4_right_x'], 14.25, 'blue'),
    # (4, 13, 'red'): (bracket_64_rounds['round_4_right_x'], 15.55, 'red'),
    # (4, 14, 'blue'): (bracket_64_rounds['round_4_right_x'], 16.85, 'blue'),
    # (4, 14, 'red'): (bracket_64_rounds['round_4_right_x'], 18.15, 'red'),
    # (4, 15, 'blue'): (bracket_64_rounds['round_4_right_x'], 19.45, 'blue'),
    # (4, 15, 'red'): (bracket_64_rounds['round_4_right_x'], 20.75, 'red'),

    (5,  0, 'blue'): (bracket_64_rounds['round_5_left_x'],  21.1, 'blue'),
    (5,  0, 'red'): (bracket_64_rounds['round_5_left_x'],  20.4, 'red'),
    (5,  1, 'blue'): (bracket_64_rounds['round_5_left_x'],  19.8, 'blue'),
    (5,  1, 'red'): (bracket_64_rounds['round_5_left_x'],  19.1, 'red'),
    (5,  2, 'blue'): (bracket_64_rounds['round_5_left_x'],  18.5, 'blue'),
    (5,  2, 'red'): (bracket_64_rounds['round_5_left_x'],  17.8, 'red'),
    (5,  3, 'blue'): (bracket_64_rounds['round_5_left_x'],  17.2, 'blue'),
    (5,  3, 'red'): (bracket_64_rounds['round_5_left_x'],  16.5, 'red'),
    (5,  4, 'blue'): (bracket_64_rounds['round_5_left_x'],  15.9, 'blue'),
    (5,  4, 'red'): (bracket_64_rounds['round_5_left_x'],  15.2, 'red'),
    (5,  5, 'blue'): (bracket_64_rounds['round_5_left_x'],  14.6, 'blue'),
    (5,  5, 'red'): (bracket_64_rounds['round_5_left_x'],  13.9, 'red'),
    (5,  6, 'blue'): (bracket_64_rounds['round_5_left_x'],  13.3, 'blue'),
    (5,  6, 'red'): (bracket_64_rounds['round_5_left_x'],  12.6, 'red'),
    (5,  7, 'blue'): (bracket_64_rounds['round_5_left_x'],  12, 'blue'),
    (5,  7, 'red'): (bracket_64_rounds['round_5_left_x'],  11.3, 'red'),
    (5,  8, 'blue'): (bracket_64_rounds['round_5_left_x'],  10.3, 'blue'),
    (5,  8, 'red'): (bracket_64_rounds['round_5_left_x'],  9.6, 'red'),
    (5,  9, 'blue'): (bracket_64_rounds['round_5_left_x'],  9, 'blue'),
    (5,  9, 'red'): (bracket_64_rounds['round_5_left_x'],  8.3, 'red'),
    (5, 10, 'blue'): (bracket_64_rounds['round_5_left_x'], 7.7, 'blue'),
    (5, 10, 'red'): (bracket_64_rounds['round_5_left_x'], 7, 'red'),
    (5, 11, 'blue'): (bracket_64_rounds['round_5_left_x'], 6.4, 'blue'),
    (5, 11, 'red'): (bracket_64_rounds['round_5_left_x'], 5.7, 'red'),
    (5, 12, 'blue'): (bracket_64_rounds['round_5_left_x'], 5.1, 'blue'),
    (5, 12, 'red'): (bracket_64_rounds['round_5_left_x'], 4.4, 'red'),
    (5, 13, 'blue'): (bracket_64_rounds['round_5_left_x'], 3.8, 'blue'),
    (5, 13, 'red'): (bracket_64_rounds['round_5_left_x'], 3.1, 'red'),
    (5, 14, 'blue'): (bracket_64_rounds['round_5_left_x'], 2.5, 'blue'),
    (5, 14, 'red'): (bracket_64_rounds['round_5_left_x'], 1.8, 'red'),
    (5, 15, 'blue'): (bracket_64_rounds['round_5_left_x'], 1.2, 'blue'),
    (5, 15, 'red'): (bracket_64_rounds['round_5_left_x'], 0.5, 'red'),

    (5, 16, 'blue'): (bracket_64_rounds['round_5_right_x'], 21.1, 'blue'),
    (5, 16, 'red'): (bracket_64_rounds['round_5_right_x'], 20.4, 'red'),
    (5, 17, 'blue'): (bracket_64_rounds['round_5_right_x'], 19.8, 'blue'),
    (5, 17, 'red'): (bracket_64_rounds['round_5_right_x'], 19.1, 'red'),
    (5, 18, 'blue'): (bracket_64_rounds['round_5_right_x'], 18.5, 'blue'),
    (5, 18, 'red'): (bracket_64_rounds['round_5_right_x'], 17.8, 'red'),
    (5, 19, 'blue'): (bracket_64_rounds['round_5_right_x'], 17.2, 'blue'),
    (5, 19, 'red'): (bracket_64_rounds['round_5_right_x'], 16.5, 'red'),
    (5, 20, 'blue'): (bracket_64_rounds['round_5_right_x'], 15.9, 'blue'),
    (5, 20, 'red'): (bracket_64_rounds['round_5_right_x'], 15.2, 'red'),
    (5, 21, 'blue'): (bracket_64_rounds['round_5_right_x'], 14.6, 'blue'),
    (5, 21, 'red'): (bracket_64_rounds['round_5_right_x'], 13.9, 'red'),
    (5, 22, 'blue'): (bracket_64_rounds['round_5_right_x'], 13.3, 'blue'),
    (5, 22, 'red'): (bracket_64_rounds['round_5_right_x'], 12.6, 'red'),
    (5, 23, 'blue'): (bracket_64_rounds['round_5_right_x'], 12, 'blue'),
    (5, 23, 'red'): (bracket_64_rounds['round_5_right_x'], 11.3, 'red'),
    (5, 24, 'blue'): (bracket_64_rounds['round_5_right_x'], 10.3, 'blue'),
    (5, 24, 'red'): (bracket_64_rounds['round_5_right_x'], 9.6, 'red'),
    (5, 25, 'blue'): (bracket_64_rounds['round_5_right_x'], 9, 'blue'),
    (5, 25, 'red'): (bracket_64_rounds['round_5_right_x'], 8.3, 'red'),
    (5, 26, 'blue'): (bracket_64_rounds['round_5_right_x'], 7.7, 'blue'),
    (5, 26, 'red'): (bracket_64_rounds['round_5_right_x'], 7, 'red'),
    (5, 27, 'blue'): (bracket_64_rounds['round_5_right_x'], 6.4, 'blue'),
    (5, 27, 'red'): (bracket_64_rounds['round_5_right_x'], 5.7, 'red'),
    (5, 28, 'blue'): (bracket_64_rounds['round_5_right_x'], 5.1, 'blue'),
    (5, 28, 'red'): (bracket_64_rounds['round_5_right_x'], 4.4, 'red'),
    (5, 29, 'blue'): (bracket_64_rounds['round_5_right_x'], 3.8, 'blue'),
    (5, 29, 'red'): (bracket_64_rounds['round_5_right_x'], 3.1, 'red'),
    (5, 30, 'blue'): (bracket_64_rounds['round_5_right_x'], 2.5, 'blue'),
    (5, 30, 'red'): (bracket_64_rounds['round_5_right_x'], 1.8, 'red'),
    (5, 31, 'blue'): (bracket_64_rounds['round_5_right_x'], 1.2, 'blue'),
    (5, 31, 'red'): (bracket_64_rounds['round_5_right_x'], 0.5, 'red'),

    # (5, 16, 'blue'): (bracket_64_rounds['round_5_right_x'], 0.5, 'blue'),
    # (5, 16, 'red'): (bracket_64_rounds['round_5_right_x'], 1.2, 'red'),
    # (5, 17, 'blue'): (bracket_64_rounds['round_5_right_x'], 1.8, 'blue'),
    # (5, 17, 'red'): (bracket_64_rounds['round_5_right_x'], 2.5, 'red'),
    # (5, 18, 'blue'): (bracket_64_rounds['round_5_right_x'], 3.1, 'blue'),
    # (5, 18, 'red'): (bracket_64_rounds['round_5_right_x'], 3.8, 'red'),
    # (5, 19, 'blue'): (bracket_64_rounds['round_5_right_x'], 4.4, 'blue'),
    # (5, 19, 'red'): (bracket_64_rounds['round_5_right_x'], 5.1, 'red'),
    # (5, 20, 'blue'): (bracket_64_rounds['round_5_right_x'], 5.7, 'blue'),
    # (5, 20, 'red'): (bracket_64_rounds['round_5_right_x'], 6.4, 'red'),
    # (5, 21, 'blue'): (bracket_64_rounds['round_5_right_x'], 7, 'blue'),
    # (5, 21, 'red'): (bracket_64_rounds['round_5_right_x'], 7.7, 'red'),
    # (5, 22, 'blue'): (bracket_64_rounds['round_5_right_x'], 8.3, 'blue'),
    # (5, 22, 'red'): (bracket_64_rounds['round_5_right_x'], 9, 'red'),
    # (5, 23, 'blue'): (bracket_64_rounds['round_5_right_x'], 9.6, 'blue'),
    # (5, 23, 'red'): (bracket_64_rounds['round_5_right_x'], 10.3, 'red'),
    # (5, 24, 'blue'): (bracket_64_rounds['round_5_right_x'], 11.3, 'blue'),
    # (5, 24, 'red'): (bracket_64_rounds['round_5_right_x'], 12, 'red'),
    # (5, 25, 'blue'): (bracket_64_rounds['round_5_right_x'], 12.6, 'blue'),
    # (5, 25, 'red'): (bracket_64_rounds['round_5_right_x'], 13.3, 'red'),
    # (5, 26, 'blue'): (bracket_64_rounds['round_5_right_x'], 13.9, 'blue'),
    # (5, 26, 'red'): (bracket_64_rounds['round_5_right_x'], 14.6, 'red'),
    # (5, 27, 'blue'): (bracket_64_rounds['round_5_right_x'], 15.2, 'blue'),
    # (5, 27, 'red'): (bracket_64_rounds['round_5_right_x'], 15.9, 'red'),
    # (5, 28, 'blue'): (bracket_64_rounds['round_5_right_x'], 16.5, 'blue'),
    # (5, 28, 'red'): (bracket_64_rounds['round_5_right_x'], 17.2, 'red'),
    # (5, 29, 'blue'): (bracket_64_rounds['round_5_right_x'], 17.8, 'blue'),
    # (5, 29, 'red'): (bracket_64_rounds['round_5_right_x'], 18.5, 'red'),
    # (5, 30, 'blue'): (bracket_64_rounds['round_5_right_x'], 19.1, 'blue'),
    # (5, 30, 'red'): (bracket_64_rounds['round_5_right_x'], 19.8, 'red'),
    # (5, 31, 'blue'): (bracket_64_rounds['round_5_right_x'], 20.4, 'blue'),
    # (5, 31, 'red'): (bracket_64_rounds['round_5_right_x'], 21.1, 'red'),
}


def _draw_text(drawing_canvas, position, text, align='left'):
    x, y, color = position
    drawing_canvas.setFillColor(color)
    if align == 'center':
        drawing_canvas.drawCentredString(x*units.cm, y*units.cm, text)
    elif align == 'right':
        drawing_canvas.drawRightString(x*units.cm, y*units.cm, text)
    else:
        drawing_canvas.drawString(x*units.cm, y*units.cm, text)


def _draw_match(match, match_positions):
    drawing_layer = StringIO()
    drawing_canvas = canvas.Canvas(drawing_layer, pagesize=letter)
    drawing_canvas.setFont('Helvetica', 8)
    align = 'left'

    if (((2**(match.round_num-1))-1) < match.round_slot) and match.round_num > 1:
        align = 'right'
    if match.round_num == 1 and match.round_slot == 1:
        align = 'right'

    if match.round_num == 0 and match.round_slot == 0 and match.winning_team:
        text = "%s" %(match.winning_team.bracket_str(),)
        position = match_positions[(match.round_num, match.round_slot, 'winning_team')]
        _draw_text(drawing_canvas, position, text, 'center')

    if match.blue_team:
        match_positions_key = (match.round_num, match.round_slot, 'blue')
        position = match_positions[match_positions_key]
        team_text = "%s" %(match.blue_team.bracket_str(),)
        _draw_text(drawing_canvas, position, team_text, align)
    if match.red_team:
        match_positions_key = (match.round_num, match.round_slot, 'red')
        position = match_positions[match_positions_key]
        team_text = "%s" %(match.red_team.bracket_str(),)
        _draw_text(drawing_canvas, position, team_text, align)

    match_number_position = get_match_number_position(match, match_positions, align)
    _draw_text(drawing_canvas, match_number_position, str(match.number), align)

    return PdfFileReader(BytesIO(drawing_canvas.getpdfdata())).getPage(0)


def get_match_number_position(match, match_positions, align):

    """
    Gets the match number position.
    Averages the positions of the red and blue teams and adds an offset depending on alignment

    :param match: TeamMatch object
    :param match_positions: Dictionary of match positions
    :param align: string Alignment
    :return match_position: position tuple
    """
    x_offset = 0
    y_offset = 0

    round_num = match.round_num
    round_slot = match.round_slot

    blue_x, blue_y, _ = match_positions[(round_num, round_slot, 'blue')]
    red_x, red_y, _ = match_positions[(round_num, round_slot, 'red')]

    if align == 'right':
        x_offset = -1
    elif align == 'left':
        x_offset = 1

    if round_num < 2:
        y_offset = 1

    match_x = (blue_x + red_x)/2.0
    match_y = (blue_y + red_y)/2.0
    match_position = match_x + x_offset, match_y + y_offset, 'black'

    return match_position

def _draw_title(division, tournament):
    title = '%s %s' %(division.__str__(), tournament.__str__())
    drawing_layer = StringIO()
    drawing_canvas = canvas.Canvas(drawing_layer, pagesize=letter)
    drawing_canvas.setFont('Helvetica-Bold', 16)
    drawing_canvas.setFillColor('white')

    # Rectangles to remove title and url
    drawing_canvas.rect(7*units.cm, 20*units.cm, 15*units.cm, 1.5*units.cm, stroke=0, fill=1)
    drawing_canvas.rect(7*units.cm, 0*units.cm, 15*units.cm, 1.1*units.cm, stroke=0, fill=1)

    # Rectangles to remove the seeds
    drawing_canvas.rect(0*units.cm, 0*units.cm, 1*units.cm, 22*units.cm, stroke=0, fill=1)
    drawing_canvas.rect(27*units.cm, 0*units.cm, 1*units.cm, 22*units.cm, stroke=0, fill=1)

    # Rectangle to remove the winner box
    drawing_canvas.rect(11*units.cm, 2*units.cm, 6*units.cm, 2.5*units.cm, stroke=0, fill=1)
    _draw_text(drawing_canvas, (14, 2, 'black'), 'WINNER', 'center')

    # Title
    _draw_text(drawing_canvas, (14, 20.5, 'black'), title, 'center')
    return PdfFileReader(BytesIO(drawing_canvas.getpdfdata())).getPage(0)


def _get_template(filename):
    this_directory = os.path.dirname(__file__)
    return os.path.join(this_directory, filename)


def _draw_matches(output_pdf, matches):
    matches = list(matches)
    if len(matches) > 31:
        match_positions = bracket_64_positions
        base_layer_filename = _get_template('64teamsingleseeded.pdf')
    else:
        match_positions = bracket_32_positions
        base_layer_filename = _get_template('32teamsingleseeded.pdf')
    base_layer = PdfFileReader(base_layer_filename).getPage(0)
    division = matches[0].division
    tournament = division.tournament
    base_layer.mergePage(_draw_title(division, tournament))
    for match in matches:
        base_layer.mergePage(_draw_match(match, match_positions))
    output_pdf.addPage(base_layer)


def _draw_position(position):
    align = 'left'
    position_key, position_value = position
    num, slot, color = position_key
    drawing_layer = StringIO()
    drawing_canvas = canvas.Canvas(drawing_layer, pagesize=letter)
    drawing_canvas.setFont('Helvetica', 10)
    if (((2**(num-1))-1) < slot) and num > 1:
        align = 'right'
    if (num == 1 and slot == 1):
        align = 'right'

    if num == 0 and slot == 0 and position_key[2] == 'winning_team':
        align = 'center'

    _draw_text(drawing_canvas, position_value, str(position_key), align)
    return PdfFileReader(BytesIO(drawing_canvas.getpdfdata())).getPage(0)

def _draw_positions(output_pdf, bracket_size):
    if bracket_size == 32:
        match_positions = bracket_32_positions
        base_layer_filename = _get_template('32teamsingleseeded.pdf')
    elif bracket_size == 64:
        match_positions = bracket_64_positions
        base_layer_filename = _get_template('64teamsingleseeded.pdf')
    else:
        raise ArgumentError('bracket_size=%d must be 32 or 64' %(bracket_size))

    base_layer = PdfFileReader(base_layer_filename).getPage(0)
    base_layer.mergePage(_draw_title('Division', 'Tournament'))
    for position in match_positions.items():
        base_layer.mergePage(_draw_position(position))
    output_pdf.addPage(base_layer)

def create_bracket_pdf(matches):
    output_pdf = PdfFileWriter()

    _draw_matches(output_pdf, matches)
    # _draw_positions(output_pdf, 32)
    # _draw_positions(output_pdf, 64)
    output_stream = BytesIO()
    output_pdf.write(output_stream)
    output_stream.flush()
    output_stream.seek(0)
    return output_stream

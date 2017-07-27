"""
Fields Model

Last Updated: 07-25-2017
"""

from django.db import models
from django.core.exceptions import ValidationError


class SexField(models.CharField):
    FEMALE = 'F'
    MALE = 'M'
    SEX_CHOICES = (
        (FEMALE, 'Female'),
        (MALE, 'Male'),
    )

    SEX_LABELS = dict(SEX_CHOICES)
    SEX_VALUES = {v.lower():k for k,v in SEX_LABELS.items()}

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 1
        kwargs['choices'] = SexField.SEX_CHOICES
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if not value in SexField.SEX_LABELS:
            raise(ValidationError("Invalid SexField value: " + value))
        return value

    @staticmethod
    def label(l):
        return SexField.SEX_LABELS[l]

    @staticmethod
    def value(v):
        return SexField.SEX_VALUES[v.lower()]

class DivisionLevelField(models.CharField):
    A_TEAM_VAL = 'A'
    B_TEAM_VAL = 'B'
    C_TEAM_VAL = 'C'
    DIVISION_LEVEL_CHOICES = (
        (A_TEAM_VAL, 'A-team'),
        (B_TEAM_VAL, 'B-team'),
        (C_TEAM_VAL, 'C-team'),
    )

    DIVISION_LEVEL_LABELS = dict(DIVISION_LEVEL_CHOICES)
    DIVISION_LEVEL_VALUES = {v.lower():k for k,v in DIVISION_LEVEL_LABELS.items()}

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 1
        kwargs['choices'] = DivisionLevelField.DIVISION_LEVEL_CHOICES
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if not value in DivisionLevelField.DIVISION_LEVEL_LABELS:
            raise(ValidationError("Invalid DivisionLevelField value: "
                    + value))
        return value

    @staticmethod
    def label(l):
        return DivisionLevelField.DIVISION_LEVEL_LABELS[l]

    @staticmethod
    def value(v):
        return DivisionLevelField.DIVISION_LEVEL_VALUES[v.lower()]

class BeltRankField(models.CharField):
    WHITE = 'WH'
    YELLOW = 'YL'
    ORANGE = 'OR'
    GREEN = 'GR'
    BLUE = 'BL'
    PURPLE = 'PL'
    BROWN = 'BR'
    RED = 'RD'
    BLACK = 'BK'
    BELT_RANK_CHOICES = (
        (WHITE, 'White'),
        (YELLOW, 'Yellow'),
        (ORANGE, 'Orange'),
        (GREEN, 'Green'),
        (BLUE, 'Blue'),
        (PURPLE, 'Purple'),
        (BROWN, 'Brown'),
        (RED, 'Red'),
        (BLACK, 'Black'),
    )

    BELT_RANK_LABELS = dict(BELT_RANK_CHOICES)
    BELT_RANK_VALUES = {v.lower():k for k,v in BELT_RANK_LABELS.items()}

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 2
        kwargs['choices'] = BeltRankField.BELT_RANK_CHOICES
        return super().__init__(*args, **kwargs)

    def to_python(self, value):
        if not value in BeltRankField.BELT_RANK_LABELS:
            raise(ValidationError("Invalid BeltRankField value: "
                    + value))
        return value

    @staticmethod
    def label(l):
        return BeltRankField.BELT_RANK_LABELS[l]

    @staticmethod
    def value(v):
        return BeltRankField.BELT_RANK_VALUES[v.lower()]

class WeightField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 4
        kwargs['decimal_places'] = 1
        super(WeightField, self).__init__(*args, **kwargs)


class ConfigurationSetting(models.Model):
    key = models.TextField(unique=True)
    value = models.TextField()
    REGISTRATION_CREDENTIALS = 'registration_credentials'
"""
Tournament Model

Last Updated: 07-25-2017
"""

# Django imports
from django.db import models
from django.db.utils import IntegrityError
from django.template.defaultfilters import slugify
# Model imports
from .fields_model import *
from django.apps import apps
# Other imports
from itertools import product

class Tournament(models.Model):
    slug = models.SlugField(unique=True)
    location = models.CharField(max_length=127)
    date = models.DateField()
    registration_doc_url = models.URLField(unique=True)
    imported = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.division_model = apps.get_model('tmdb', 'Division')
        self.tournament_division_model = apps.get_model('tmdb', 'TournamentDivision')
        self.school_registration_model = apps.get_model('tmdb', 'SchoolRegistration')
        self.school_model = apps.get_model('tmdb', 'School')

    def save(self, *args, **kwargs):
        self.slug = self.slugify()
        new_tournament = not self.id

        super(Tournament, self).save(*args, **kwargs)

        if new_tournament:
            self.create_divisions()

    def slugify(self):
        return slugify(self.location) + '-' + slugify(self.date)

    def create_divisions(self):
        sex_labels = SexField.SEX_LABELS
        skill_labels = DivisionLevelField.DIVISION_LEVEL_LABELS
        for sex, skill_level in product(sex_labels, skill_labels):
            division = self.division_model.objects.filter(sex=sex,
                    skill_level=skill_level).first()
            if division is None:
                division = self.division_model(sex=sex, skill_level=skill_level)
                division.clean()
                division.save()
            td = self.tournament_division_model(tournament=self, division=division)
            td.clean()
            td.save()

    def __str__(self):
        return "%s Tournament (%s)" %(
                self.location, self.date.strftime("%Y %b %d"))

    def __repr__(self):
        return self.slug if self.slug else self.slugify()

    def download_registration(self):
        """Downloads registration spreadsheet from registration_doc_url."""
        from ectc_registration import GoogleDocsDownloader
        from ectc_registration import GoogleDriveSpreadsheet
        from ectc_registration import RegistrationExtractor

        try:
            creds = ConfigurationSetting.objects.get(
                    key=ConfigurationSetting.REGISTRATION_CREDENTIALS).value
        except ConfigurationSetting.DoesNotExist:
            raise IntegrityError("Registration credentials have not been"
                    + " provided")
        doc_url = self.registration_doc_url
        doc_key = GoogleDocsDownloader.extract_file_id(doc_url)
        downloader = GoogleDocsDownloader(creds_json=creds)
        workbook = GoogleDriveSpreadsheet(downloader, doc_key)
        reg_extractor = RegistrationExtractor(workbook)
        return reg_extractor.get_registration_workbooks()

    def save_downloaded_school(self, school):
        school_object = self.school_model.objects.filter(
                name=school.school_name).first()
        if school_object is None:
            school_object = self.school_model(name=school.school_name)
            school_object.clean()
            school_object.save()
        registration = self.school_registration_model(tournament=self,
                school=school_object,
                registration_doc_url=school.registration_doc_url)
        registration.clean()
        registration.save()

    def save_downloaded_schools(self, schools):
        for school in schools:
            self.save_downloaded_school(school)

    def import_school_registrations(self):
        """Imports a school's registration information from
        registration_doc_url."""
        if self.imported:
            raise IntegrityError(("%s is already imported" %(self)
                    + " - and cannot be imported again"))
        registered_schools = self.download_registration()
        self.save_downloaded_schools(registered_schools)

        self.imported = True
        self.save()
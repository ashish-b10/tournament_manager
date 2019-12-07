#!/usr/bin/env python3
from datetime import date
import logging

from django.core.management.base import BaseCommand

from tmdb import models
from tmdb.tests import TournamentImportTestCase

class LoadSampleTmdbData():
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        TournamentImportTestCase.import_all_tournaments(verbose=True)

class Command(BaseCommand):
    help = 'Loads test data into the database - useful for testing the UI'

    def handle(self, *args, **options):
        LoadSampleTmdbData()

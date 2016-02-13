#!/usr/bin/env python3
from django.core.management.base import BaseCommand
import tmdb.models as mdls
from datetime import date

class LoadSampleTmdbData():
    def __init__(self):
        self.add_tournaments()

    def add_tournaments(self):
        # registration_doc_urls are just nonsense placefillers
        self.mit2015 = mdls.Tournament(date=date(year=2015, month=10, day=11),
                location="MIT",
                registration_doc_url="http://ectc-online.org/mit-2015")
        self.mit2015.save()
        self.cornell2015 = mdls.Tournament(date=date(year=2015, month=11,
                day=1), location="Cornell",
                registration_doc_url="http://ectc-online.org/cornell-2015")
        self.cornell2015.save()

class Command(BaseCommand):
    help = 'Loads test data into the database - useful for testing the UI'

    def handle(self, *args, **options):
        LoadSampleTmdbData()

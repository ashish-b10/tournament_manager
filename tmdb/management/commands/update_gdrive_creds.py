from django.core.management.base import BaseCommand
from tmdb.models import ConfigurationSetting as tmdb_config
import argparse

import sys

class Command(BaseCommand):
    help = 'Utility commands to get, set and delete Google Drive credentials'

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument('-d', '--drop', action='store_true',
                help="Drop the existing credentials from the database")
        group.add_argument('-g', '--get', action='store_true',
                help="Get and print the existing credentials from the database")
        group.add_argument('-f', '--file',
            help='Read the credentials from a file and save them to the database')

    def get_key(self, verbosity=1):
        key = tmdb_config.objects.filter(
                key=tmdb_config.REGISTRATION_CREDENTIALS).first()
        if key is None and verbosity > 0:
            self.stderr.write("Could not find credentials in database")
        return key

    def handle(self, *args, **options):
        if options['get']:
            key = self.get_key(options['verbosity'])
            if key:
                print(key.value)
            return
        if options['drop']:
            key = self.get_key(options['verbosity'])
            if key:
                key.delete()
            return
        creds_file = options['file']
        if creds_file:
            try:
                with open(creds_file) as creds_fh:
                    creds = creds_fh.read()
            except IOError as e:
                if options['verbosity'] > 0:
                    self.stderr.write("Unable to open %s: %s" %(creds_file,e))
                sys.exit(1)
            tmdb_config.objects.update_or_create(
                    key=tmdb_config.REGISTRATION_CREDENTIALS, value=creds)
            if options['verbosity'] > 0:
                self.stdout.write("Successfully imported credentials from "
                        + creds_file)
            return

from django.core.management.base import BaseCommand
from django.contrib.auth import models as auth_models
from tmdb.models import ConfigurationSetting as tmdb_config
from tmdb.views.settings_view import get_headtable_permission_group
import argparse

import sys

class Command(BaseCommand):
    help = 'Utility commands to get, set and delete Google Drive credentials'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username', type=str, help="Username")
        parser.add_argument('-p', '--password', type=str, help="Password")

    def handle(self, *args, **options):
        user = auth_models.User.objects.create_user(
                username=options['username'], password=options['password'])
        user.groups.set([get_headtable_permission_group()])

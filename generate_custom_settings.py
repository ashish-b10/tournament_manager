#!/usr/bin/python

from pathlib import Path

from django.core.management.utils import get_random_secret_key

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_random_secret_key()
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Write out the python file
output_file = Path(__file__).parent / 'ectc_tm_server' / 'custom_settings.py'
with open(output_file, "w") as fh:
    fh.write("SECRET_KEY=\"" + SECRET_KEY +"\"\n")
    fh.write("DEBUG=" + str(DEBUG) + "\n")
    fh.write("ALLOWED_HOSTS = [\"localhost\"]\n")

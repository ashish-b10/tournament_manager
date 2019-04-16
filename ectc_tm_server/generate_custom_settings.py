#!/usr/bin/python

from django.core.management.utils import get_random_secret_key

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_random_secret_key()
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Write out the python file
file = open("custom_settings.py","w")
file.write("SECRET_KEY=\"" + SECRET_KEY +"\"\n")
file.write("DEBUG=" + str(DEBUG) + "\n")
file.write("ALLOWED_HOSTS = ['www.ectc-tournaments.org', 'ectc-tournaments.org', '198.98.59.77']\n")
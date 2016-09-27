This document outlines how to set up tmdb to use PostgreSQL on Ubuntu or any other Debian-derived distro.

# Installation

    sudo apt-get install postgresql postgresql-contrib

# Running

Installation should automatically start PostgreSQL and configure it to start on boot-up. However, to be sure it is running, execute

    sudo /etc/init.d/postgresql start

# Configuration

At a minimum for development purposes, it is necessary to create a username and database for the tmdb user, and configure the tmdb user to connect locally. In order to run unit tests, it will also be necessary to grant permission to create and delete databases as the tmdb user.

Note that these instructions are woefully unsecure for use on a production server and should not be used as such.

First, create the user and database (may require root privileges):

    createuser tmdb -d
    createdb tmdb

Next, the pg_hba.conf file must be edited to allow local access for the tmdb user. The location of pg_hba.conf can vary, but should usually be found in a location like /etc/postgresql/9.3/main/

Add the following lines to the file. It is recommended that these be the first non-commented lines as earlier lines take precedence over later ones:

    # "local" is for Unix domain socket connections only
    local   all             user                                    trust
    # IPv4 local connections:
    host    all             tmdb            127.0.0.1/32            trust
    # IPv6 local connections:
    host    all             tmdb            ::1/128                 trust

In order for these changes to take effect, restart the service:

    /etc/init.d/postgresql restart

# Python Bindings

Django's implementation of the PostgreSQL backend requires the following packages to be installed:

    pip3 install psycopg2 pelican

Alternatively, uncomment the relevant portions of requirements.txt and reinstall it using

    pip3 install -r requirements.txt

If the above installations fail, then it might be necessary to install the following packages:

    sudo apt-get install postgresql postgresql-contrib libffi-dev

# Django Configuration

Modify the DATABASES variable in ectc_tm_server/settings.py as follows:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'tmdb',
            'USER': 'tmdb',
            'HOST': 'localhost',
        }
    }

# Next steps

At this point, PostgreSQL is fully set up for Django. Start by creating migrations and applying them:

    python manage.py makemigrations && python manage.py migrate

and now you should be ready to go. Happy Hacking!

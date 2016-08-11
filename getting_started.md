# Getting Started

This document details how to set up and run an instance of the ECTC Tournament Manager. It is not (yet) a user interface guide.

## Recommended Knowledge
`tmdb` primarily makes use of Django, which is a Python framework for creating web applications (a database which exists on the server and HTML views to interact with the database). Users do not need to have a complete understanding of Django to use the software (though it certainly does not hurt!).

For developers, it is very simple to get started with Django - the introductory tutorial is a great place to start, and very easy to understand - it can accessed here: https://docs.djangoproject.com/en/1.10/intro/tutorial01/ The tutorial teaches how the database is structured using Django's built-in Object-Relational Mapper, how changes to the database can be managed via migrations, how to use the controller interface which Django automatically creates when you develop the ORM, and how to use its built-in templating interface for dynamically generating views.

## Database Backend

By default, the application is configured to use SQLite as a backend because of its ease of setup - it requires fewer additional dependencies and saves the developer from having to configure access permissions. However, it is intended that the production server will use PostgreSQL as a backend, thus it is helpful to know how to set up PostgreSQL and configure Django (and `tmdb`) to use it. While using SQLite is easier than PostgreSQL, there is a very small chance that features which work with PostgreSQL do not work with SQLite and an even smaller chance that features working with SQLite do not work with PostgreSQL.

As a result of the above considerations, this tutorial will provide instruction in setting up for SQLite. Setup instructions for PostgreSQL can be found in [postgresql.md](postgresql.md).

More information on Django backends can be found here: https://docs.djangoproject.com/en/1.10/#the-model-layer

## Using Python 3

The application is written using Python 3.x. Users and developers should take care to ensure that they are using this version of Python and not 2.x.

# Installing the Requisite Software

## Python (Required)

Most Linux distributions provide Python by default, but not all provide Python 3, so take care to ensure that's the version you're using.

This tutorial will provide most instructions in Bash, so Cygwin is recommended for Windows developers, but not at all necessary for those who feel comfortable configuring their Python and database environment. Instructions on how to install Cygwin are not provided here, but again, all developers must take care to ensure that they are using Python 3.

You can run

    python3 --version

to make sure that you are using Python 3.

### Creating a Python Virtualenv (Recommended)

A virtualenv is recommended, but not required, as doing so keeps `tmdb` development and dependencies separate from the root Python installation. virtualenv is generally not provided with Python by default, but can be installed as follows:

    easy_install virtualenv

Root privileges may be required for this command to work.

Then to create a virtualenv, run:

    virtualenv -p $(which python3) tmdb_local/

This will create a copy of your Python installation into a directory called `tmdb_local/` (you are free to change this to any directory you like, of course). Having a copy of your Python installation will allow you to install Python dependencies into a location that's specific to `tmdb` development. It is only required to execute this command once. Then every time you wish to start Python development, you must execute:

    source tmdb_local/bin/activate

for all active terminal sessions.

## Python dependencies

If the source code has not been cloned already, then clone it:

    git clone https://github.com/ashish-b10/tournament_manager.git

Make sure the virtualenv is already loaded:

    source tmdb_local/bin/activate

And then install the requirements:

    pip3 install -r tournament_manager/requirements.txt

### ectc-registration

One of the project dependencies which is also managed by the ECTC is ectc-registration: [https://github.com/ashish-b10/ectc_registration]. This package requires credentials JSON file in order to work properly. This credential file should be saved ouside the code repository so it is not added by accident.

Once the credentials have been downloaded, they can be tested by running the below command:

    python -m ectc_registration.gdocs_downloader -c /path/to/credentials.json -u (INSERT LINK TO A GOOGLE SPREADSHEET)

If the credentials are valid, this command should download a spreadsheet and report some statistics on it.

If you get an error of `SignedJwtAssertionCredentials`, you have to `pip install ouathclient=1.5.2`.

# Run the service

If this is the first time running the `tmdb`, the database must be created.

To make model migrations:

    python manage.py makemigrations tmdb

To run the server locally,

    python manage.py runserver

If there are ever any changes to the models.py file, you will have to reset the database. You can do this by doing either:

    rm -r tmdb/migrations ; dropdb tmdb && createdb tmdb && python manage.py makemigrations tmdb && python manage.py migrate && python manage.py add_test_data or simply run `bash ./reset_db.sh`.

# Updating the Database

Django's built in ORM is responsible for interfacing with the database. From time to time, changes on the server will require that the database be updated. Currently, the only way to do this is to delete the database and recreate it. Take care to note that ALL DATA IN THE DATABASE WILL BE LOST, though it can be backed up beforehand. Once ready, update the database as follows:

    rm -r tmdb/migrations ; dropdb tmdb && createdb tmdb && python manage.py makemigrations tmdb && python manage.py migrate && python manage.py add_test_data && python manage.py graph_models -g -o /dev/shm/tmdb.svg tmdb && python manage.py runserver

And don't forget to re-import your Google Drive credentials!

    python manage.py update_gdrive_creds -f /path/to/credentials.json
